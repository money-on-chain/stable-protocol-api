from fastapi import APIRouter, HTTPException, Path, Query
from typing import Annotated, Optional

from api import registry, voting
from api.logger import log
from api.db import get_db
from api.models.voting import \
    VotingProposalList, \
    VotingProposalDetail, \
    UserVotingList, \
    VotingStats, \
    MipEntryList, \
    MipContent

from .common import make_responses
from .omoc import require_db, get_last_block_indexed


tags_metadata = [{
    "name": "Voting",
    "description": "OMoC VotingMachine proposal history, rebuilt from the "
                   "indexed voting events, and the MIP documents of the "
                   "proposal registry (money-on-chain/proposals-changers)"}]


router = APIRouter(tags=["Voting"])

ADDRESS_PATTERN = '^0x[a-fA-F0-9]{40}$'

# Records are paginated in memory, so a negative skip would slice from the end
LimitQuery = Annotated[int, Query(title="Limit", description="Limit", ge=1, le=100)]
SkipQuery = Annotated[int, Query(title="Skip", description="Skip", ge=0, le=1000)]

ProposalPath = Annotated[str, Path(
    title="Proposal address",
    description="The proposal (ChangeContract) address",
    pattern=ADDRESS_PATTERN)]
UserPath = Annotated[str, Path(
    title="User address",
    description="Address that pre-voted or voted: the user's wallet, or its "
                "vesting contract for vesting holders",
    pattern=ADDRESS_PATTERN)]
MipPath = Annotated[str, Path(
    title="MIP",
    description="MIP number, as MIP263101 or 263101",
    pattern='^(MIP|mip)?[0-9]{6}$')]
StatusQuery = Annotated[Optional[str], Query(
    title="Status",
    description="Optional filter by status: " + ", ".join(voting.STATUSES),
    pattern="^(" + "|".join(voting.STATUSES) + ")$")]
ProposerQuery = Annotated[Optional[str], Query(
    title="Proposer address",
    description="Optional filter by the address that submitted the proposal",
    pattern=ADDRESS_PATTERN)]
TagQuery = Annotated[Optional[str], Query(
    title="Tag",
    description="Optional filter: MIPs tagged with this project "
                "(doc, usdrif, oracles, voting, staking)",
    pattern="^[a-z0-9-]{1,32}$")]
NetworkQuery = Annotated[Optional[str], Query(
    title="Network",
    description="Overrides the API's network (GOVERNANCE_NETWORK): " +
                ", ".join(registry.NETWORKS),
    pattern="^(" + "|".join(registry.NETWORKS) + ")$")]
ListedQuery = Annotated[Optional[bool], Query(
    title="Listed",
    description="Optional filter: true for proposals in the proposal registry, "
                "false for unlisted ones")]


async def registry_or_none():
    """The proposal registry, or None when it can't be read: proposal history
    is still served, with `listed` left unknown."""
    try:
        return await registry.get_registry()
    except registry.RegistryUnavailable as e:
        log.warning(f"Serving voting history without the registry: {e}")
        return None


async def require_registry():
    try:
        value = await registry.get_registry()
    except registry.RegistryUnavailable:
        raise HTTPException(status_code=503, detail="Proposal registry unavailable")
    if value is None:
        raise HTTPException(status_code=404, detail="Proposal registry disabled")
    return value


async def with_executions(entries):
    """The entries with their execution (registry.with_execution): one query
    for the indexed AcceptedStepEvents of all their changers. Without DB the
    registry's executedTx is used alone."""
    executions = {}
    try:
        db = await get_db()
        if db is not None:
            executions = await voting.changer_executions(
                db, [c["address"] for e in entries for c in e["changers"]])
    except Exception as e:
        log.warning(f"Serving MIPs without indexed executions: {e}")
    return [registry.with_execution(e, executions) for e in entries]


async def mip_content(entry):
    try:
        document = await registry.get_document(entry)
    except registry.RegistryUnavailable:
        raise HTTPException(status_code=503, detail="Proposal document unavailable")
    return {**entry, **document}


@router.get(
    "/api/v1/omoc/voting/proposals/",
    response_description="Returns the proposals history, newest round first",
    response_model=VotingProposalList,
    responses=make_responses(503),
)
async def voting_proposals(
        status: StatusQuery = None,
        proposer: ProposerQuery = None,
        listed: ListedQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns one record per proposal and voting round - a proposal
    pre-voted again in a later round has one record per round - with its
    pre-vote and vote tallies (wei strings), its steps' transactions, status
    and MIP. `listed` is false for changers not in the proposal registry."""
    db = await require_db()
    records = registry.annotate(
        await voting.build_proposal_records(db), await registry_or_none())
    if status:
        records = [r for r in records if r["status"] == status]
    if proposer:
        records = [r for r in records if r["proposer"] == proposer.lower()]
    if listed is not None:
        records = [r for r in records if r["listed"] is listed]
    page = records[skip:skip + limit]
    return {
        "results": page,
        "count": len(page),
        "total": len(records),
        "last_block_indexed": await get_last_block_indexed(db),
    }


@router.get(
    "/api/v1/omoc/voting/proposals/{address}/",
    response_description="Returns a proposal's records, timeline and voters",
    response_model=VotingProposalDetail,
    responses=make_responses(404, 503),
)
async def voting_proposal(address: ProposalPath):
    """Returns every record of a proposal with its milestones (submitted,
    selected for voting, voting closed, execution) and who pre-voted and voted
    it, one row per user and round, largest stake first (up to 500 each)."""
    db = await require_db()
    proposal = address.lower()
    records = await voting.build_proposal_records(db, proposal=proposal)
    if not records:
        raise HTTPException(status_code=404, detail="Not found")
    registry.annotate(records, await registry_or_none())
    voters, pre_voters = await voting.proposal_participants(db, proposal)
    return {
        "proposal": proposal,
        "records": records,
        "timeline": voting.proposal_timeline(records),
        "voters": voters,
        "preVoters": pre_voters,
        "last_block_indexed": await get_last_block_indexed(db),
    }


@router.get(
    "/api/v1/omoc/voting/proposals/{address}/content/",
    response_description="Returns the MIP document of a proposal",
    response_model=MipContent,
    responses=make_responses(404, 503),
)
async def voting_proposal_content(address: ProposalPath):
    """Returns the registry entry and markdown document of the MIP the changer
    was submitted for; 404 when the changer is not in the registry. Relative
    images and links are made absolute: only show images under
    `assetsBaseUrl`, and render the markdown without raw HTML."""
    entries = await require_registry()
    entry = entries["byAddress"].get(address.lower())
    if entry is None:
        raise HTTPException(status_code=404, detail="Not found")
    return await mip_content(entry)


@router.get(
    "/api/v1/omoc/voting/mips/",
    response_description="Returns the proposal registry, newest MIP first",
    response_model=MipEntryList,
    responses=make_responses(503),
)
async def voting_mips(
        network: NetworkQuery = None,
        tag: TagQuery = None,
        limit: LimitQuery = 100,
        skip: SkipQuery = 0):
    """Returns the MIPs of the proposal registry that have a changer on the
    API's network (GOVERNANCE_NETWORK, or `network`), with only that network's
    changers. Drafts are not listed; `tag` keeps the MIPs tagged with it. Lists every non-draft MIP when no network
    is configured."""
    entries = await require_registry()
    network = network or registry.NETWORK
    results = [e for e in (registry.listable(e, network)
                           for e in entries["byMip"].values()) if e]
    if tag:
        results = [e for e in results if tag in e["tags"]]
    results.sort(key=lambda e: e["mip"], reverse=True)
    page = await with_executions(results[skip:skip + limit])
    return {"results": page, "count": len(page), "total": len(results)}


@router.get(
    "/api/v1/omoc/voting/mips/{mip}/",
    response_description="Returns a MIP's registry entry and document",
    response_model=MipContent,
    responses=make_responses(404, 503),
)
async def voting_mip(mip: MipPath, network: NetworkQuery = None):
    """Returns a MIP's registry entry and markdown document, like
    /proposals/{address}/content/ but looked up by MIP number. 404 for a
    draft, or when the MIP has no changer on the API's network
    (GOVERNANCE_NETWORK, or `network`)."""
    entries = await require_registry()
    entry = entries["byMip"].get(registry.normalize_mip(mip))
    if entry is not None:
        entry = registry.listable(entry, network or registry.NETWORK)
    if entry is None:
        raise HTTPException(status_code=404, detail="Not found")
    [entry] = await with_executions([entry])
    return await mip_content(entry)


@router.get(
    "/api/v1/omoc/voting/users/{address}/",
    response_description="Returns the proposals a user pre-voted or voted",
    response_model=UserVotingList,
    responses=make_responses(503),
)
async def voting_user(
        address: UserPath,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the proposal records the address took part in, newest round
    first, each with what the address pre-voted and voted on it."""
    db = await require_db()
    user = address.lower()
    participation = await voting.user_participation(db, user)
    records = registry.annotate(
        await voting.build_proposal_records(db, keys=set(participation)),
        await registry_or_none())
    for rec in records:
        rec["participation"] = {
            **participation.get((rec["proposal"], rec["round"]), {}),
            "isProposer": rec["proposer"] == user,
        }
    page = records[skip:skip + limit]
    return {
        "results": page,
        "count": len(page),
        "total": len(records),
        "last_block_indexed": await get_last_block_indexed(db),
    }


@router.get(
    "/api/v1/omoc/voting/stats/",
    response_description="Returns governance participation statistics",
    response_model=VotingStats,
    responses=make_responses(503),
)
async def voting_stats():
    """Returns proposal counts by status, unique participants and a summary
    of every round that reached voting, oldest first."""
    db = await require_db()
    stats = await voting.voting_stats(db)
    registry.annotate(stats["votingRounds"], await registry_or_none())
    stats["last_block_indexed"] = await get_last_block_indexed(db)
    return stats
