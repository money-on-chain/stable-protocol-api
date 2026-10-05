"""
Proposal registry: the MIP documents behind the on-chain proposals.

money-on-chain/proposals-changers keeps every proposal as a markdown document
(docs/proposals/MIPxxxxxx-*.md) indexed by docs/proposals/proposals.json, which
lists each MIP's title, status, summary, forum link and the changer contracts
submitted for it. That repo's CI validates the registry (unique MIPs, EIP-55
addresses, changers matching the documents and ignition deployments).

A changer voted on-chain is matched to its MIP by address. One that is not in
the registry is reported as unlisted: preVote() is open to any staker, so an
unlisted changer was not submitted through the MIP process.

The registry and documents are fetched from the repo (raw.githubusercontent.com
by default) and cached in-process - the API's mongo user may be read-only. On a
failed refresh the last good copy keeps being served.

Until the VotingMachine emits its voting events on a network (on mainnet, from
MIP#263501 on), the indexed history is empty there and the registry's MIPs with
a changer on the API's network are the list of proposals to show.

Env:
  GOVERNANCE_REGISTRY_URL  url of proposals.json (empty disables the registry).
                           Documents and images are resolved relative to it.
  GOVERNANCE_NETWORK       network this API serves, as named in the registry
                           (rskMainnet / rskTestnet): MIPs are listed only when
                           they have a changer there. Empty lists every MIP.
"""

import asyncio
import datetime
import json
import re
import time
from os import getenv
from urllib.parse import urljoin

import httpx

from api.logger import log


REGISTRY_URL = getenv(
    "GOVERNANCE_REGISTRY_URL",
    default="https://raw.githubusercontent.com/money-on-chain/proposals-changers/"
            "proposals_registry/docs/proposals/proposals.json")

NETWORKS = ("rskMainnet", "rskTestnet")
NETWORK = getenv("GOVERNANCE_NETWORK", default="") or None
if NETWORK is not None and NETWORK not in NETWORKS:
    raise ValueError(f"GOVERNANCE_NETWORK must be one of {', '.join(NETWORKS)}")

TTL = 300
MAX_REGISTRY_BYTES = 1024 * 1024
MAX_DOCUMENT_BYTES = 1024 * 1024
REQUEST_TIMEOUT = 8

_RAW_GITHUB = re.compile(
    r"^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/(.+)$")
_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")
_MIP = re.compile(r"^(?:MIP#?)?(\d{6})$", re.IGNORECASE)
# ![alt](target "title") and [text](target), not inside code spans
_IMAGE = re.compile(r"(!\[[^\]]*\]\()\s*<?([^)\s>]+)>?((?:\s+\"[^\"]*\")?\s*\))")
_LINK = re.compile(r"((?<!!)\[[^\]]*\]\()\s*<?([^)\s>]+)>?((?:\s+\"[^\"]*\")?\s*\))")
_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:|^//|^#")

_registry = {"expires": 0.0, "value": None}
_documents = {}
_registry_lock = asyncio.Lock()


class RegistryUnavailable(Exception):
    pass


def normalize_mip(value):
    """'MIP#263101', 'MIP263101' or '263101' -> 'MIP#263101' (None if not a MIP)."""
    match = _MIP.match(value or "")
    return f"MIP#{match.group(1)}" if match else None


def on_network(entry, network):
    """The entry with only its changers on `network`, or None when it has
    none there. A falsy `network` keeps every entry and changer."""
    if not network:
        return entry
    changers = [c for c in entry["changers"] if c["network"] == network]
    return {**entry, "changers": changers} if changers else None


def listable(entry, network):
    """The entry as the mips endpoints serve it: drafts are not shown, and
    only MIPs with a changer on `network` (see on_network)."""
    if entry.get("status") == "Draft":
        return None
    return on_network(entry, network)


def _html_url(raw_url):
    """Browsable url of a raw.githubusercontent.com file, for document links."""
    match = _RAW_GITHUB.match(raw_url)
    if not match:
        return raw_url
    owner, repo, ref_and_path = match.groups()
    return f"https://github.com/{owner}/{repo}/blob/{ref_and_path}"


async def _get(client, url, max_bytes):
    try:
        async with client.stream("GET", url) as response:
            if response.status_code == 404:
                return None
            if response.status_code != 200:
                raise RegistryUnavailable(f"GET {url} -> {response.status_code}")
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body += chunk
                if len(body) > max_bytes:
                    raise RegistryUnavailable(f"GET {url} -> over {max_bytes} bytes")
            return bytes(body)
    except httpx.HTTPError as e:
        raise RegistryUnavailable(f"{type(e).__name__}: {e}") from e


def _client():
    return httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True,
                             headers={"User-Agent": "stable-protocol-api"})


def _entry(raw):
    """Registry entry as served by the API, or None when malformed."""
    if not isinstance(raw, dict):
        return None
    mip = normalize_mip(raw.get("mip"))
    file = raw.get("file")
    if not mip or not isinstance(file, str) or "/" in file or not file.endswith(".md"):
        return None
    changers = []
    for changer in raw.get("changers") or []:
        if isinstance(changer, dict) and _ADDRESS.match(str(changer.get("address"))):
            submitter = changer.get("submitter")
            changers.append({
                "network": changer.get("network"),
                "name": changer.get("name"),
                "address": changer["address"],
                # First preVote() sender; None until submitted
                "submitter": submitter
                if _ADDRESS.match(str(submitter)) else None,
            })
    document_url = urljoin(REGISTRY_URL, file)
    tags = raw.get("tags")
    return {
        "mip": mip,
        "title": raw.get("title"),
        # Projects the MIP changes (doc, usdrif, oracles, ...); the registry's
        # validator owns the vocabulary
        "tags": [t for t in tags if isinstance(t, str)]
        if isinstance(tags, list) else [],
        "status": raw.get("status"),
        "date": raw.get("date"),
        "summary": raw.get("summary"),
        "forumUrl": raw.get("forumUrl"),
        "file": file,
        "documentUrl": _html_url(document_url),
        "changers": changers,
    }


async def _fetch_registry():
    async with _client() as client:
        body = await _get(client, REGISTRY_URL, MAX_REGISTRY_BYTES)
    if body is None:
        raise RegistryUnavailable(f"{REGISTRY_URL} not found")
    try:
        data = json.loads(body)
    except ValueError as e:
        raise RegistryUnavailable(f"invalid registry json: {e}") from e

    by_mip = {}
    by_address = {}
    proposals = data.get("proposals") if isinstance(data, dict) else None
    for raw in proposals or []:
        entry = _entry(raw)
        if entry is None:
            log.warning(f"Skipping malformed registry entry: {raw!r:.200}")
            continue
        by_mip[entry["mip"]] = entry
        for changer in entry["changers"]:
            by_address[changer["address"].lower()] = entry
    return {"byMip": by_mip, "byAddress": by_address}


async def get_registry():
    """{'byMip': {mip: entry}, 'byAddress': {lowercase changer: entry}}, or
    None when the registry is disabled. Raises RegistryUnavailable only when
    there is no cached copy to fall back to."""
    if not REGISTRY_URL:
        return None
    if _registry["value"] is not None and _registry["expires"] > time.monotonic():
        return _registry["value"]
    async with _registry_lock:
        if _registry["value"] is not None and _registry["expires"] > time.monotonic():
            return _registry["value"]
        try:
            value = await _fetch_registry()
        except RegistryUnavailable as e:
            log.warning(f"Proposal registry refresh failed: {e}")
            if _registry["value"] is None:
                raise
            # Serve the last good copy, retry after a short while
            _registry["expires"] = time.monotonic() + 60
            return _registry["value"]
        _registry.update(value=value, expires=time.monotonic() + TTL)
        return value


def _rewrite_links(markdown, document_url):
    """Absolute urls for the document's relative images and links. Returns the
    markdown and the urls of its images stored next to the document."""
    images = []
    assets_base = urljoin(document_url, ".")

    def image(match):
        target = match.group(2)
        if not _SCHEME.match(target):
            target = urljoin(document_url, target)
        # Only the repo's own images; the dapp shows nothing else
        if target.startswith(assets_base):
            images.append(target)
        return f"{match.group(1)}{target}{match.group(3)}"

    def link(match):
        target = match.group(2)
        if not _SCHEME.match(target):
            target = _html_url(urljoin(document_url, target))
        return f"{match.group(1)}{target}{match.group(3)}"

    # Leave fenced code blocks untouched
    parts = re.split(r"(```[\s\S]*?```)", markdown)
    for i in range(0, len(parts), 2):
        parts[i] = _LINK.sub(link, _IMAGE.sub(image, parts[i]))
    return "".join(parts), list(dict.fromkeys(images))


async def get_document(entry):
    """The entry's markdown with absolute links: {'markdown', 'images',
    'fetchedAt'}. Raises RegistryUnavailable when it can't be fetched."""
    document_url = urljoin(REGISTRY_URL, entry["file"])
    cached = _documents.get(document_url)
    if cached and cached[0] > time.monotonic():
        return cached[1]

    async with _client() as client:
        body = await _get(client, document_url, MAX_DOCUMENT_BYTES)
    if body is None:
        raise RegistryUnavailable(f"{document_url} not found")
    markdown, images = _rewrite_links(body.decode("utf-8", "replace"), document_url)
    value = {
        "markdown": markdown,
        "images": images,
        "assetsBaseUrl": urljoin(document_url, "."),
        "fetchedAt": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    }
    # Documents are few (one per MIP), so the cache needs no eviction
    # beyond its TTL.
    _documents[document_url] = (time.monotonic() + TTL, value)
    return value


def annotate(records, registry):
    """Adds the registry fields to proposal records in place."""
    for rec in records:
        entry = registry["byAddress"].get(rec["proposal"]) if registry else None
        rec["listed"] = None if registry is None else entry is not None
        rec["mip"] = entry["mip"] if entry else None
        rec["title"] = entry["title"] if entry else None
        rec["summary"] = entry["summary"] if entry else None
        rec["forumUrl"] = entry["forumUrl"] if entry else None
    return records
