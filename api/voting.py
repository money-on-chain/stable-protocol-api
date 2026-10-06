"""
Historic VotingMachine proposals, rebuilt from the indexed OMoC events.

Every VotingMachine event carries the voting `round`, and at most one proposal
per round leaves pre-voting (PreVoteStepEvent) to be voted, so a
(proposal, round) pair identifies one pass of a ChangeContract through the
machine. The same address can be pre-voted again in a later round, so a
proposal address may own several records.

Amounts are wei strings on the events. They are summed in mongo as Decimal128
(exact up to 34 significant digits) and returned as integer strings. Pre-vote
and vote stakes are additive on-chain - a repeated preVote()/vote() only emits
the stake not locked yet - so these sums match the contract's own tallies.

Vetoes (VetoMachine) and the total supply at the time of a round are not part
of these events: a vetoed proposal is only known through its VoteStep result.
"""

from bson.decimal128 import Decimal128

from api.utils import mongo_date_to_str


PRE_VOTE = "event_VotingMachine_PreVoteEvent"
VOTE = "event_VotingMachine_VoteEvent"
PRE_VOTE_STEP = "event_VotingMachine_PreVoteStepEvent"
VOTE_STEP = "event_VotingMachine_VoteStepEvent"
ACCEPTED_STEP = "event_VotingMachine_AcceptedStepEvent"
UNREGISTER = "event_VotingMachine_UnregisterEvent"

# VotingMachineStorage.ProposalResult (0 = None is never emitted)
VOTE_RESULTS = {1: "Accepted", 2: "NoQuorum", 3: "Vetoed"}

# Lifecycle of a (proposal, round) record:
#   PreVoting      candidate in the current round's pre-vote (it may have
#                  expired on-chain; the expiration is not part of the events)
#   Unregistered   withdrawn from the round's pre-vote
#   NotSelected    another proposal of the same round went to voting
#   Voting         selected for voting, no result yet
#   Accepted       voted in, waiting for acceptedStep() to execute it
#   NoQuorum / Vetoed
#   Executed / ExecutionFailed   acceptedStep() outcome
STATUSES = (
    "PreVoting", "Unregistered", "NotSelected", "Voting", "Accepted",
    "NoQuorum", "Vetoed", "Executed", "ExecutionFailed",
)

MAX_PARTICIPANTS = 500

_ZERO = {"$toDecimal": 0}
_LOG_INDEX = {"$toInt": {"$arrayElemAt": [{"$split": ["$id_event", ":"]}, 1]}}


def wei_str(value) -> str:
    if isinstance(value, Decimal128):
        value = value.to_decimal()
    return str(int(value or 0))


def _event_order(doc):
    try:
        log_index = int(doc.get("id_event", "").split(":")[1])
    except (IndexError, ValueError):
        log_index = 0
    return doc.get("blockNumber") or 0, log_index


def _tx(doc) -> dict:
    return {
        "hash": doc.get("hash"),
        "blockNumber": doc.get("blockNumber"),
        "createdAt": mongo_date_to_str(doc.get("createdAt")),
    }


async def _pre_vote_totals(db, match):
    """(proposal, round) -> pre-vote sum, pre-voters and the first pre-voter,
    who is the proposer (preVote() records proposalProposer on the first vote
    of a round)."""
    pipeline = [
        {"$match": match},
        {"$addFields": {"logIndex": _LOG_INDEX}},
        {"$sort": {"blockNumber": 1, "logIndex": 1}},
        {"$group": {
            "_id": {"proposal": "$proposal", "round": "$round"},
            "votes": {"$sum": {"$toDecimal": "$stake"}},
            "voters": {"$addToSet": "$user"},
            "first": {"$first": "$$ROOT"},
            "lastAt": {"$max": "$createdAt"},
        }},
    ]
    out = {}
    async for row in db[PRE_VOTE].aggregate(pipeline, allowDiskUse=True):
        key = (row["_id"]["proposal"], row["_id"]["round"])
        out[key] = {
            "votes": wei_str(row["votes"]),
            "voters": len(row["voters"]),
            "voterSet": set(row["voters"]),
            "proposer": row["first"].get("user"),
            "submitted": row["first"],
            "lastAt": row["lastAt"],
        }
    return out


async def _vote_totals(db, match):
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": {"proposal": "$proposal", "round": "$round"},
            "inFavor": {"$sum": {"$cond": [
                "$inFavorAgainst", {"$toDecimal": "$stake"}, _ZERO]}},
            "against": {"$sum": {"$cond": [
                "$inFavorAgainst", _ZERO, {"$toDecimal": "$stake"}]}},
            "voters": {"$addToSet": "$user"},
            "lastAt": {"$max": "$createdAt"},
        }},
    ]
    out = {}
    async for row in db[VOTE].aggregate(pipeline, allowDiskUse=True):
        key = (row["_id"]["proposal"], row["_id"]["round"])
        in_favor = int(wei_str(row["inFavor"]))
        against = int(wei_str(row["against"]))
        out[key] = {
            "inFavor": str(in_favor),
            "against": str(against),
            "total": str(in_favor + against),
            "voters": len(row["voters"]),
            "voterSet": set(row["voters"]),
            "lastAt": row["lastAt"],
        }
    return out


async def _last_step_events(db, collection, match):
    """(proposal, round) -> latest event of a step collection."""
    out = {}
    async for doc in db[collection].find(match):
        key = (doc["proposal"], doc["round"])
        if key not in out or _event_order(doc) > _event_order(out[key]):
            out[key] = doc
    return out


def _status(key, pre_vote, pre_vote_step, vote_step, accepted_step,
            unregister, round_winners):
    if key in accepted_step:
        return "Executed" if accepted_step[key].get("success") else "ExecutionFailed"
    if key in vote_step:
        return VOTE_RESULTS.get(vote_step[key].get("result"), "Voting")
    if key in pre_vote_step:
        return "Voting"
    if key in unregister:
        submitted = pre_vote.get(key)
        # preVote() can register the proposal again after an unregister
        if submitted is None or _event_order(unregister[key]) > _event_order(
                submitted.get("lastEvent", submitted["submitted"])):
            return "Unregistered"
    if key[1] in round_winners:
        return "NotSelected"
    return "PreVoting"


async def build_proposal_records(db, proposal=None, keys=None, proposals=None):
    """All (proposal, round) records, newest round first. `proposal` limits
    them to one ChangeContract address, `proposals` to a list of them and
    `keys` to a set of (proposal, round)."""
    match = {"proposal": proposal} if proposal else {}
    if proposals is not None:
        proposals = {p.lower() for p in proposals}
        if not proposals:
            return []
        match = {"proposal": {"$in": sorted(proposals)}}
    if keys is not None:
        if not keys:
            return []
        match = {"$or": [{"proposal": p, "round": r} for p, r in keys]}

    pre_vote = await _pre_vote_totals(db, match)
    votes = await _vote_totals(db, match)
    vote_step = await _last_step_events(db, VOTE_STEP, match)
    accepted_step = await _last_step_events(db, ACCEPTED_STEP, match)
    unregister = await _last_step_events(db, UNREGISTER, match)
    # All winners (one per round), not only the matched ones: a candidate that
    # lost its round's pre-vote is told apart by another proposal's step.
    all_pre_vote_steps = await _last_step_events(db, PRE_VOTE_STEP, {})
    pre_vote_step = {k: v for k, v in all_pre_vote_steps.items()
                     if (not proposal or k[0] == proposal)
                     and (proposals is None or k[0] in proposals)
                     and (keys is None or k in keys)}
    round_winners = {r: p for p, r in all_pre_vote_steps}

    # Last pre-vote per key, to order it against an unregister of that key
    if unregister:
        async for doc in db[PRE_VOTE].find({"$or": [
                {"proposal": p, "round": r} for p, r in unregister]}):
            key = (doc["proposal"], doc["round"])
            entry = pre_vote.get(key)
            if entry is not None and (
                    "lastEvent" not in entry
                    or _event_order(doc) > _event_order(entry["lastEvent"])):
                entry["lastEvent"] = doc

    all_keys = (set(pre_vote) | set(votes) | set(pre_vote_step)
                | set(vote_step) | set(accepted_step) | set(unregister))

    records = []
    for key in all_keys:
        pv = pre_vote.get(key)
        vt = votes.get(key)
        steps = [d for d in (
            pv["submitted"] if pv else None,
            pre_vote_step.get(key), vote_step.get(key),
            accepted_step.get(key), unregister.get(key)) if d]
        dates = [d.get("createdAt") for d in steps if d.get("createdAt")]
        dates += [x["lastAt"] for x in (pv, vt) if x and x.get("lastAt")]

        pvs = pre_vote_step.get(key)
        vs = vote_step.get(key)
        acs = accepted_step.get(key)
        unr = unregister.get(key)
        # preVoteStep() starts the voting with the winner's pre-vote support
        # as votes in favor (VotingDataLib._startVoting); vote() only adds to
        # it, so a proposal can pass without a single VoteEvent.
        from_pre_vote = int(pvs.get("votesInFavor") or 0) if pvs else 0
        in_favor = from_pre_vote + int(vt["inFavor"] if vt else 0)
        against = int(vt["against"] if vt else 0)
        supporters = ((pv["voterSet"] if pv else set())
                      | (vt["voterSet"] if vt else set()))
        records.append({
            "proposal": key[0],
            "round": key[1],
            "status": _status(key, pre_vote, pre_vote_step, vote_step,
                              accepted_step, unregister, round_winners),
            "proposer": pv["proposer"] if pv else None,
            "createdAt": mongo_date_to_str(min(dates)) if dates else None,
            "updatedAt": mongo_date_to_str(max(dates)) if dates else None,
            "preVote": {
                "votes": pv["votes"] if pv else "0",
                "voters": pv["voters"] if pv else 0,
                "submitted": _tx(pv["submitted"]) if pv else None,
            },
            "preVoteStep": {**_tx(pvs), "votesInFavor": pvs.get("votesInFavor")}
            if pvs else None,
            # Tallies as the contract counts them: inFavor includes the
            # support carried from pre-voting (fromPreVote), voters counts
            # only the voting phase and supporters every address that
            # pre-voted or voted the proposal in this round.
            "vote": {
                "inFavor": str(in_favor),
                "against": str(against),
                "total": str(in_favor + against),
                "fromPreVote": str(from_pre_vote),
                "voters": vt["voters"] if vt else 0,
                "supporters": len(supporters),
            },
            "voteStep": {**_tx(vs), "result": vs.get("result"),
                         "resultLabel": VOTE_RESULTS.get(vs.get("result"))}
            if vs else None,
            "acceptedStep": {**_tx(acs), "success": acs.get("success")}
            if acs else None,
            "unregister": _tx(unr) if unr else None,
        })

    # Newest round first; inside a round the winner first, then by support
    records.sort(key=lambda r: (
        -r["round"],
        r["preVoteStep"] is None,
        -int(r["preVote"]["votes"]),
        r["proposal"]))
    return records


async def proposal_participants(db, proposal):
    """Voters and pre-voters of a proposal, one row per (user, round), largest
    stake first."""
    voters = []
    pipeline = [
        {"$match": {"proposal": proposal}},
        {"$group": {
            "_id": {"user": "$user", "round": "$round"},
            "inFavor": {"$sum": {"$cond": [
                "$inFavorAgainst", {"$toDecimal": "$stake"}, _ZERO]}},
            "against": {"$sum": {"$cond": [
                "$inFavorAgainst", _ZERO, {"$toDecimal": "$stake"}]}},
            "total": {"$sum": {"$toDecimal": "$stake"}},
            "txs": {"$sum": 1},
            "last": {"$max": {"createdAt": "$createdAt", "hash": "$hash"}},
        }},
        {"$sort": {"total": -1}},
        {"$limit": MAX_PARTICIPANTS},
    ]
    async for row in db[VOTE].aggregate(pipeline, allowDiskUse=True):
        voters.append({
            "user": row["_id"]["user"],
            "round": row["_id"]["round"],
            "inFavor": wei_str(row["inFavor"]),
            "against": wei_str(row["against"]),
            "txs": row["txs"],
            "lastHash": row["last"].get("hash"),
            "lastAt": mongo_date_to_str(row["last"].get("createdAt")),
        })

    pre_voters = []
    pipeline = [
        {"$match": {"proposal": proposal}},
        {"$group": {
            "_id": {"user": "$user", "round": "$round"},
            "stake": {"$sum": {"$toDecimal": "$stake"}},
            "txs": {"$sum": 1},
            "last": {"$max": {"createdAt": "$createdAt", "hash": "$hash"}},
        }},
        {"$sort": {"stake": -1}},
        {"$limit": MAX_PARTICIPANTS},
    ]
    async for row in db[PRE_VOTE].aggregate(pipeline, allowDiskUse=True):
        pre_voters.append({
            "user": row["_id"]["user"],
            "round": row["_id"]["round"],
            "stake": wei_str(row["stake"]),
            "txs": row["txs"],
            "lastHash": row["last"].get("hash"),
            "lastAt": mongo_date_to_str(row["last"].get("createdAt")),
        })

    return voters, pre_voters


def proposal_timeline(records):
    """Milestones of every record of a proposal, oldest first."""
    milestones = []
    for rec in records:
        steps = (
            ("Submitted", rec["preVote"]["submitted"], {"user": rec["proposer"]}),
            ("SelectedForVoting", rec["preVoteStep"], {}),
            ("VotingClosed", rec["voteStep"], {}),
            ("ExecutionAttempted", rec["acceptedStep"], {}),
            ("Unregistered", rec["unregister"], {}),
        )
        for kind, step, extra in steps:
            if not step:
                continue
            item = {"type": kind, "round": rec["round"],
                    "hash": step["hash"], "blockNumber": step["blockNumber"],
                    "createdAt": step["createdAt"], **extra}
            if kind == "VotingClosed":
                item["result"] = step["resultLabel"]
            if kind == "ExecutionAttempted":
                item["success"] = step["success"]
            milestones.append(item)
    milestones.sort(key=lambda m: (m["blockNumber"] or 0, m["round"]))
    return milestones


async def user_participation(db, user):
    """(proposal, round) -> what `user` pre-voted and voted on it."""
    out = {}
    pipeline = [
        {"$match": {"user": user}},
        {"$group": {
            "_id": {"proposal": "$proposal", "round": "$round"},
            "stake": {"$sum": {"$toDecimal": "$stake"}},
        }},
    ]
    async for row in db[PRE_VOTE].aggregate(pipeline):
        key = (row["_id"]["proposal"], row["_id"]["round"])
        out.setdefault(key, {})["preVote"] = wei_str(row["stake"])

    pipeline = [
        {"$match": {"user": user}},
        {"$group": {
            "_id": {"proposal": "$proposal", "round": "$round"},
            "inFavor": {"$sum": {"$cond": [
                "$inFavorAgainst", {"$toDecimal": "$stake"}, _ZERO]}},
            "against": {"$sum": {"$cond": [
                "$inFavorAgainst", _ZERO, {"$toDecimal": "$stake"}]}},
        }},
    ]
    async for row in db[VOTE].aggregate(pipeline):
        key = (row["_id"]["proposal"], row["_id"]["round"])
        entry = out.setdefault(key, {})
        entry["voteInFavor"] = wei_str(row["inFavor"])
        entry["voteAgainst"] = wei_str(row["against"])
    return out


async def latest_changer_records(db, addresses):
    """Lowercase changer -> its newest (proposal, round) record: the latest
    attempt of each changer in the VotingMachine."""
    latest = {}
    for rec in await build_proposal_records(db, proposals=addresses):
        prev = latest.get(rec["proposal"])
        if prev is None or rec["round"] > prev["round"]:
            latest[rec["proposal"]] = rec
    return latest


async def changer_executions(db, addresses):
    """Lowercase changer -> {"hash", "createdAt"} of the acceptedStep() that
    executed it successfully, from the indexed AcceptedStepEvents."""
    addresses = [a.lower() for a in addresses]
    if not addresses:
        return {}
    out = {}
    cursor = db[ACCEPTED_STEP].find(
        {"proposal": {"$in": addresses}, "success": True})
    async for doc in cursor:
        prev = out.get(doc["proposal"])
        if prev is None or _event_order(doc) < prev["order"]:
            out[doc["proposal"]] = {
                "hash": doc.get("hash"),
                "createdAt": mongo_date_to_str(doc.get("createdAt")),
                "order": _event_order(doc),
            }
    return {k: {"hash": v["hash"], "createdAt": v["createdAt"]}
            for k, v in out.items()}


async def voting_stats(db):
    records = await build_proposal_records(db)

    status_counts = {status: 0 for status in STATUSES}
    for rec in records:
        status_counts[rec["status"]] += 1

    rounds = []
    for rec in sorted(records, key=lambda r: r["round"]):
        if rec["preVoteStep"] is None:
            continue
        rounds.append({
            "round": rec["round"],
            "proposal": rec["proposal"],
            "status": rec["status"],
            "preVoteVotes": rec["preVote"]["votes"],
            "inFavor": rec["vote"]["inFavor"],
            "against": rec["vote"]["against"],
            "voters": rec["vote"]["voters"],
            "votingStartedAt": rec["preVoteStep"]["createdAt"],
            "votingClosedAt": rec["voteStep"]["createdAt"]
            if rec["voteStep"] else None,
        })

    voters = set(await db[VOTE].distinct("user"))
    pre_voters = set(await db[PRE_VOTE].distinct("user"))

    return {
        "proposals": len({rec["proposal"] for rec in records}),
        "records": len(records),
        "rounds": len({rec["round"] for rec in records}),
        "reachedVoting": len(rounds),
        "statusCounts": status_counts,
        "uniqueVoters": len(voters),
        "uniquePreVoters": len(pre_voters),
        "uniqueParticipants": len(voters | pre_voters),
        "votingRounds": rounds,
    }
