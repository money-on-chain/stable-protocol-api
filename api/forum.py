"""
Proposal write-ups from the governance forum (Discourse).

A proposal only exists on-chain as its ChangeContract address; the human
description is a forum topic whose first post lists that address in its
"Changer Contract" section. The forum sends no CORS headers, so the API looks
the topic up server-side: Discourse search by address, then the candidate whose
first post has the address inside a "Changer ..." section wins (a later MIP can
mention an older changer elsewhere), oldest topic first on a tie.

Results are cached in-process only: the API's mongo user may be read-only, and
a lookup is a couple of small requests, so every API task keeping its own cache
is cheap.

Env:
  GOVERNANCE_FORUM_URL     forum base url (empty disables the lookup)
  GOVERNANCE_FORUM_TOPICS  JSON {"<changer address>": <topic id>} for proposals
                           the search can't resolve (no post, ambiguous, ...)
"""

import asyncio
import datetime
import json
import re
import time
from os import getenv

import httpx

from api.logger import log


FORUM_URL = getenv("GOVERNANCE_FORUM_URL",
                   default="https://forum.moneyonchain.com").rstrip("/")

FOUND_TTL = 6 * 3600
MISSING_TTL = 30 * 60
MAX_CACHE_ENTRIES = 2000
MAX_CANDIDATES = 5
REQUEST_TIMEOUT = 8

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
_MIP = re.compile(r"MIP#\s*(\d+)")
_FORUM_STATUS = re.compile(
    r"Status:\s*[*_`\s]*([A-Za-z][A-Za-z ]*?)[*_`\s]*$", re.MULTILINE)

_cache = {}
_locks = {}


class ForumUnavailable(Exception):
    pass


def _topic_overrides():
    raw = getenv("GOVERNANCE_FORUM_TOPICS")
    if not raw:
        return {}
    try:
        return {k.lower(): int(v) for k, v in json.loads(raw).items()}
    except (ValueError, TypeError, AttributeError):
        log.warning("GOVERNANCE_FORUM_TOPICS is not a JSON object of "
                    "address -> topic id, ignoring it")
        return {}


TOPIC_OVERRIDES = _topic_overrides()


def _changer_section(raw):
    """Text of the first heading section whose title mentions 'changer',
    up to the next heading of the same or a higher level."""
    headings = list(_HEADING.finditer(raw))
    for i, match in enumerate(headings):
        if "changer" not in match.group(2).lower():
            continue
        level = len(match.group(1))
        end = len(raw)
        for nxt in headings[i + 1:]:
            if len(nxt.group(1)) <= level:
                end = nxt.start()
                break
        return raw[match.end():end]
    return ""


def _score(raw, address):
    if address in _changer_section(raw).lower():
        return 2
    if address in raw.lower():
        return 1
    return 0


async def _get(client, path, **params):
    try:
        response = await client.get(f"{FORUM_URL}{path}", params=params or None)
    except httpx.HTTPError as e:
        raise ForumUnavailable(f"{type(e).__name__}: {e}") from e
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise ForumUnavailable(f"GET {path} -> {response.status_code}")
    return response


async def _first_post_raw(client, topic_id):
    response = await _get(client, f"/raw/{topic_id}/1")
    return response.text if response is not None else None


async def _resolve_topic(client, address):
    """(topic id, first post raw) for `address`, or None."""
    override = TOPIC_OVERRIDES.get(address)
    if override is not None:
        raw = await _first_post_raw(client, override)
        return (override, raw) if raw is not None else None

    response = await _get(client, "/search.json", q=address)
    if response is None:
        return None
    topic_ids = [t["id"] for t in response.json().get("topics", [])
                 if isinstance(t.get("id"), int)][:MAX_CANDIDATES]

    best = None
    for topic_id in sorted(topic_ids):
        raw = await _first_post_raw(client, topic_id)
        if raw is None:
            continue
        score = _score(raw, address)
        if score == 2:
            return topic_id, raw
        if score and best is None:
            best = (topic_id, raw)
    return best


async def _fetch(address):
    async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "stable-protocol-api",
                     "Accept": "application/json"}) as client:
        resolved = await _resolve_topic(client, address)
        if resolved is None:
            return None
        topic_id, raw = resolved

        response = await _get(client, f"/t/{topic_id}.json")
        topic = response.json() if response is not None else {}

    slug = topic.get("slug")
    mip = _MIP.search(raw)
    forum_status = _FORUM_STATUS.search(raw)
    return {
        "proposal": address,
        "topicId": topic_id,
        "title": topic.get("title"),
        "url": f"{FORUM_URL}/t/{slug}/{topic_id}" if slug
        else f"{FORUM_URL}/t/{topic_id}",
        "mip": f"MIP#{mip.group(1)}" if mip else None,
        "forumStatus": forum_status.group(1).strip() if forum_status else None,
        "createdAt": topic.get("created_at"),
        "raw": raw,
        "fetchedAt": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    }


def _cache_put(address, value):
    now = time.monotonic()
    if len(_cache) >= MAX_CACHE_ENTRIES:
        for key in [k for k, (expires, _) in _cache.items() if expires <= now]:
            del _cache[key]
        if len(_cache) >= MAX_CACHE_ENTRIES:
            _cache.clear()
    _cache[address] = (now + (FOUND_TTL if value else MISSING_TTL), value)


async def get_proposal_content(address):
    """Forum write-up of a proposal, or None when there is none. Raises
    ForumUnavailable when the forum can't be reached (not cached)."""
    address = address.lower()
    if not FORUM_URL:
        return None

    cached = _cache.get(address)
    if cached and cached[0] > time.monotonic():
        return cached[1]

    # One lookup per address at a time; concurrent callers wait for it and
    # then read the cache. Dropped afterwards so arbitrary addresses can't
    # grow this dict.
    lock = _locks.setdefault(address, asyncio.Lock())
    try:
        async with lock:
            cached = _cache.get(address)
            if cached and cached[0] > time.monotonic():
                return cached[1]
            try:
                value = await _fetch(address)
            except ForumUnavailable as e:
                log.warning(f"Governance forum lookup for {address} failed: {e}")
                raise
            _cache_put(address, value)
            return value
    finally:
        if _locks.get(address) is lock and not lock.locked():
            del _locks[address]
