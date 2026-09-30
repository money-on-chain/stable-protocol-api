from fastapi import APIRouter, HTTPException, Path, Query
from typing import Annotated, Optional

from api import forum, voting
from api.models.voting import \
    VotingProposalList, \
    VotingProposalDetail, \
    UserVotingList, \
    VotingStats, \
    ProposalContent

from .common import make_responses
from .omoc import require_db, get_last_block_indexed


tags_metadata = [{
    "name": "Voting",
    "description": "OMoC VotingMachine proposal history, rebuilt from the "
                   "indexed voting events, and the proposals' governance "
                   "forum write-ups"}]


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
StatusQuery = Annotated[Optional[str], Query(
    title="Status",
    description="Optional filter by status: " + ", ".join(voting.STATUSES),
    pattern="^(" + "|".join(voting.STATUSES) + ")$")]
ProposerQuery = Annotated[Optional[str], Query(
    title="Proposer address",
    description="Optional filter by the address that submitted the proposal",
    pattern=ADDRESS_PATTERN)]


@router.get(
    "/api/v1/omoc/voting/proposals/",
    response_description="Returns the proposals history, newest round first",
    response_model=VotingProposalList,
    responses=make_responses(503),
)
async def voting_proposals(
        status: StatusQuery = None,
        proposer: ProposerQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns one record per proposal and voting round - a proposal
    pre-voted again in a later round has one record per round - with its
    pre-vote and vote tallies (wei strings), its steps' transactions and
    status."""
    db = await require_db()
    records = await voting.build_proposal_records(db)
    if status:
        records = [r for r in records if r["status"] == status]
    if proposer:
        records = [r for r in records if r["proposer"] == proposer.lower()]
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
    response_description="Returns the proposal's governance forum write-up",
    response_model=ProposalContent,
    responses=make_responses(404, 503),
)
async def voting_proposal_content(address: ProposalPath):
    """Returns the forum topic describing the proposal: its first post as raw
    markdown plus the title, MIP number and forum status parsed from it. The
    markdown is forum content - render it without raw HTML."""
    try:
        content = await forum.get_proposal_content(address)
    except forum.ForumUnavailable:
        raise HTTPException(status_code=503,
                            detail="Governance forum unavailable")
    if content is None:
        raise HTTPException(status_code=404, detail="Not found")
    return content


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
    records = await voting.build_proposal_records(
        db, keys=set(participation))
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
    stats["last_block_indexed"] = await get_last_block_indexed(db)
    return stats
