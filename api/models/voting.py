from pydantic import BaseModel
from typing import Dict, Optional, List


class VotingTx(BaseModel):
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    createdAt: Optional[str] = None


class PreVoteTally(BaseModel):
    votes: str = "0"
    voters: int = 0
    submitted: Optional[VotingTx] = None


class PreVoteStep(VotingTx):
    votesInFavor: Optional[str] = None


class VoteTally(BaseModel):
    inFavor: str = "0"
    against: str = "0"
    total: str = "0"
    voters: int = 0


class VoteStep(VotingTx):
    result: Optional[int] = None
    resultLabel: Optional[str] = None


class AcceptedStep(VotingTx):
    success: Optional[bool] = None


class VotingProposal(BaseModel):
    proposal: str
    round: int
    status: str
    proposer: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    preVote: PreVoteTally
    preVoteStep: Optional[PreVoteStep] = None
    vote: VoteTally
    voteStep: Optional[VoteStep] = None
    acceptedStep: Optional[AcceptedStep] = None
    unregister: Optional[VotingTx] = None

    class Config:
        json_schema_extra = {
            "example": {
                "proposal": "0xbe8c4d532969586616a6cfe33f4094858af22026",
                "round": 13,
                "status": "Executed",
                "proposer": "0xf3aedc384d880eae53d198551868c3574f10ec42",
                "createdAt": "2026-09-02T01:41:31.000Z",
                "updatedAt": "2026-09-02T03:32:21.000Z",
                "preVote": {
                    "votes": "15000001969999999999999998",
                    "voters": 1,
                    "submitted": {
                        "hash": "0xd82ba3f1d354b54940de0c7e6b6546f4db0f22d478c0bfa0d89860dbf4cafe06",
                        "blockNumber": 8033220,
                        "createdAt": "2026-09-02T01:41:31.000Z"}},
                "preVoteStep": {
                    "hash": "0xaf967084da56adb4dce2e1696be44eb585f5449ee357f4226a0289192c815432",
                    "blockNumber": 8033254,
                    "createdAt": "2026-09-02T01:56:00.000Z",
                    "votesInFavor": "15000001969999999999999998"},
                "vote": {"inFavor": "15000001969999999999999998",
                         "against": "0",
                         "total": "15000001969999999999999998",
                         "voters": 1},
                "voteStep": {
                    "hash": "0x8e877a8de9588eba2c437806f60a598d41f3fbc98f232086388552274f2a1df1",
                    "blockNumber": 8033315,
                    "createdAt": "2026-09-02T02:17:36.000Z",
                    "result": 1,
                    "resultLabel": "Accepted"},
                "acceptedStep": {
                    "hash": "0x131bda47a7b247c0deb0df159ce720f8a5f5cf110100e5de377ec9751736a911",
                    "blockNumber": 8033497,
                    "createdAt": "2026-09-02T03:32:21.000Z",
                    "success": True},
                "unregister": None
            }
        }


class VotingProposalList(BaseModel):
    results: List[VotingProposal]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0


class VotingMilestone(BaseModel):
    type: str
    round: int
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    createdAt: Optional[str] = None
    user: Optional[str] = None
    result: Optional[str] = None
    success: Optional[bool] = None


class ProposalVoter(BaseModel):
    user: str
    round: int
    inFavor: str = "0"
    against: str = "0"
    txs: int = 0
    lastHash: Optional[str] = None
    lastAt: Optional[str] = None


class ProposalPreVoter(BaseModel):
    user: str
    round: int
    stake: str = "0"
    txs: int = 0
    lastHash: Optional[str] = None
    lastAt: Optional[str] = None


class VotingProposalDetail(BaseModel):
    proposal: str
    records: List[VotingProposal]
    timeline: List[VotingMilestone]
    voters: List[ProposalVoter]
    preVoters: List[ProposalPreVoter]
    last_block_indexed: int = 0


class UserParticipation(BaseModel):
    preVote: str = "0"
    voteInFavor: str = "0"
    voteAgainst: str = "0"
    isProposer: bool = False


class UserVotingRecord(VotingProposal):
    participation: UserParticipation


class UserVotingList(BaseModel):
    results: List[UserVotingRecord]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0


class VotingRoundSummary(BaseModel):
    round: int
    proposal: str
    status: str
    preVoteVotes: str = "0"
    inFavor: str = "0"
    against: str = "0"
    voters: int = 0
    votingStartedAt: Optional[str] = None
    votingClosedAt: Optional[str] = None


class VotingStats(BaseModel):
    proposals: int = 0
    records: int = 0
    rounds: int = 0
    reachedVoting: int = 0
    statusCounts: Dict[str, int]
    uniqueVoters: int = 0
    uniquePreVoters: int = 0
    uniqueParticipants: int = 0
    votingRounds: List[VotingRoundSummary]
    last_block_indexed: int = 0


class ProposalContent(BaseModel):
    proposal: str
    topicId: int
    title: Optional[str] = None
    url: str
    mip: Optional[str] = None
    forumStatus: Optional[str] = None
    createdAt: Optional[str] = None
    raw: str
    fetchedAt: str
