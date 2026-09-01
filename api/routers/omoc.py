from fastapi import APIRouter, Query, HTTPException
from typing import Annotated, Optional

from api.db import get_db, CASE_INSENSITIVE_COLLATION
from api.models.omoc import DATE_FIELDS, \
    fields_date_to_str, \
    VestingCreatedList, \
    ClaimOKList, \
    DelayMachinePaymentCancelList, \
    DelayMachinePaymentDepositList, \
    DelayMachinePaymentWithdrawList, \
    SupportersAddStakeList, \
    SupportersCancelEarningsList, \
    SupportersPayEarningsList, \
    SupportersWithdrawList, \
    SupportersWithdrawStakeList, \
    VotingMachinePreVoteEventList, \
    VotingMachineVoteEventList, \
    VotingMachinePreVoteStepEventList, \
    VotingMachineVoteStepEventList, \
    VotingMachineAcceptedStepEventList, \
    VotingMachineUnregisterEventList, \
    OracleManagerOracleRegisteredList, \
    OracleManagerOracleStakeAddedList, \
    OracleManagerOracleSubscribedList, \
    OracleManagerOracleUnsubscribedList, \
    OracleManagerOracleRemovedList, \
    CoinPairPricePricePublishedList, \
    CoinPairPriceEmergencyPricePublishedList, \
    CoinPairPriceForcedPriceQueryModeSetList, \
    CoinPairPriceOracleRewardTransferList, \
    CoinPairPriceNewRoundList, \
    CoinPairPriceOracleAutoUnsubscribedList

from .common import make_responses


tags_metadata = [{
    "name": "OMoC",
    "description": "On-chain Money on Chain governance: staking, vesting, "
                   "delay machine, voting machine, oracle manager and "
                   "decentralized oracle (CoinPairPrice) events"}]


router = APIRouter(tags=["OMoC"])

LimitQuery = Annotated[int, Query(title="Limit", description="Limit", le=100)]
SkipQuery = Annotated[int, Query(title="Skip", description="Skip", le=1000)]
HolderQuery = Annotated[str, Query(
    title="Holder address",
    description="Holder Address",
    regex='^0x[a-fA-F0-9]{40}$')]
AddressFilterQuery = Annotated[Optional[str], Query(
    title="Address",
    description="Optional filter matching the given address against any of the "
                "event's address fields",
    regex='^0x[a-fA-F0-9]{40}$')]
ProposalQuery = Annotated[Optional[str], Query(
    title="Proposal address",
    description="Optional filter by the proposal (ChangeContract) address",
    regex='^0x[a-fA-F0-9]{40}$')]
CallerQuery = Annotated[Optional[str], Query(
    title="Caller address",
    description="Optional filter by the caller address",
    regex='^0x[a-fA-F0-9]{40}$')]
CoinPairAddressQuery = Annotated[Optional[str], Query(
    title="Coin pair address",
    description="Optional filter by the CoinPairPrice contract address "
                "(one deployment per coin pair)",
    regex='^0x[a-fA-F0-9]{40}$')]

DEFAULT_HOLDER = '0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3'


def address_in_any(address, fields):
    """Filter matching `address` against any of the given address fields."""
    if not address:
        return None
    return {"$or": [{field: address} for field in fields]}


async def require_db():
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Cannot get DB access")
    return db


async def get_last_block_indexed(db) -> int:
    indexer = await db["moc_indexer"].find_one(sort=[("updatedAt", -1)])
    if indexer and 'last_raw_tx_block' in indexer:
        return indexer['last_raw_tx_block']
    return 0


async def list_events(db, collection, results_key='results', *,
                      limit, skip, query_filter=None, collation=None):
    """Shared query / paginate / serialize for the OMoC event collections."""
    query_filter = query_filter or {}

    cursor = db[collection].find(query_filter)
    if collation is not None:
        cursor = cursor.collation(collation)

    rows = await cursor.sort("createdAt", -1)\
        .skip(skip)\
        .limit(limit)\
        .to_list(limit)

    count_kwargs = {"collation": collation} if collation is not None else {}
    rows_count = await db[collection].count_documents(query_filter, **count_kwargs)

    for row in rows:
        row['_id'] = str(row['_id'])
        fields_date_to_str(row, DATE_FIELDS)

    return {
        results_key: rows,
        "count": len(rows),
        "total": rows_count,
        "last_block_indexed": await get_last_block_indexed(db),
    }


# --- Vesting / Incentive --------------------------------------------------------

@router.get(
    "/api/v1/omoc/vesting_created/",
    response_description="Returns vesting created from a holder address",
    response_model=VestingCreatedList,
    responses=make_responses(503),
)
async def vesting_created(
        holder: HolderQuery = DEFAULT_HOLDER,
        limit: LimitQuery = 50,
        skip: SkipQuery = 0):
    """Returns the vesting contracts created for the given holder address."""
    db = await require_db()
    return await list_events(
        db, "event_VestingFactory_VestingCreated", "transactions",
        limit=limit, skip=skip,
        query_filter={"holder": holder},
        collation=CASE_INSENSITIVE_COLLATION)


@router.get(
    "/api/v1/omoc/claim_ok/",
    response_description="Returns incentive claims for a recipient address",
    response_model=ClaimOKList,
    responses=make_responses(503),
)
async def claim_ok(
        holder: HolderQuery = DEFAULT_HOLDER,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the incentive claim events for the given recipient address."""
    db = await require_db()
    return await list_events(
        db, "event_IncentiveV2_ClaimOK", "results",
        limit=limit, skip=skip,
        query_filter={"recipient": holder},
        collation=CASE_INSENSITIVE_COLLATION)


# --- Delay Machine ------------------------------------------------------------

@router.get(
    "/api/v1/omoc/delay_machine_payment_cancel/",
    response_description="Returns the delay machine payment cancel events",
    response_model=DelayMachinePaymentCancelList,
    responses=make_responses(503),
)
async def delay_machine_payment_cancel(
        address: AddressFilterQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the delay machine payment cancel events, optionally filtered by
    an address on either side of the payment (source or destination)."""
    db = await require_db()
    return await list_events(
        db, "event_DelayMachine_PaymentCancel", limit=limit, skip=skip,
        query_filter=address_in_any(address, ("source", "destination")),
        collation=CASE_INSENSITIVE_COLLATION if address else None)


@router.get(
    "/api/v1/omoc/delay_machine_payment_deposit/",
    response_description="Returns the delay machine payment deposit events",
    response_model=DelayMachinePaymentDepositList,
    responses=make_responses(503),
)
async def delay_machine_payment_deposit(
        address: AddressFilterQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the delay machine payment deposit events, optionally filtered by
    an address on either side of the payment (source or destination)."""
    db = await require_db()
    return await list_events(
        db, "event_DelayMachine_PaymentDeposit", limit=limit, skip=skip,
        query_filter=address_in_any(address, ("source", "destination")),
        collation=CASE_INSENSITIVE_COLLATION if address else None)


@router.get(
    "/api/v1/omoc/delay_machine_payment_withdraw/",
    response_description="Returns the delay machine payment withdraw events",
    response_model=DelayMachinePaymentWithdrawList,
    responses=make_responses(503),
)
async def delay_machine_payment_withdraw(
        address: AddressFilterQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the delay machine payment withdraw events, optionally filtered by
    an address on either side of the payment (source or destination)."""
    db = await require_db()
    return await list_events(
        db, "event_DelayMachine_PaymentWithdraw", limit=limit, skip=skip,
        query_filter=address_in_any(address, ("source", "destination")),
        collation=CASE_INSENSITIVE_COLLATION if address else None)


# --- Supporters ------------------------------------------------------------------

@router.get(
    "/api/v1/omoc/supporters_add_stake/",
    response_description="Returns the supporters add stake events",
    response_model=SupportersAddStakeList,
    responses=make_responses(503),
)
async def supporters_add_stake(
        address: AddressFilterQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the supporters add stake events, optionally filtered by an
    address (matched against user, subaccount or sender)."""
    db = await require_db()
    return await list_events(
        db, "event_Supporters_AddStake", limit=limit, skip=skip,
        query_filter=address_in_any(address, ("user", "subaccount", "sender")),
        collation=CASE_INSENSITIVE_COLLATION if address else None)


@router.get(
    "/api/v1/omoc/supporters_cancel_earnings/",
    response_description="Returns the supporters cancel earnings events",
    response_model=SupportersCancelEarningsList,
    responses=make_responses(503),
)
async def supporters_cancel_earnings(limit: LimitQuery = 20, skip: SkipQuery = 0):
    """Returns the supporters cancel earnings events."""
    db = await require_db()
    return await list_events(
        db, "event_Supporters_CancelEarnings", limit=limit, skip=skip)


@router.get(
    "/api/v1/omoc/supporters_pay_earnings/",
    response_description="Returns the supporters pay earnings events",
    response_model=SupportersPayEarningsList,
    responses=make_responses(503),
)
async def supporters_pay_earnings(limit: LimitQuery = 20, skip: SkipQuery = 0):
    """Returns the supporters pay earnings events."""
    db = await require_db()
    return await list_events(
        db, "event_Supporters_PayEarnings", limit=limit, skip=skip)


@router.get(
    "/api/v1/omoc/supporters_withdraw/",
    response_description="Returns the supporters withdraw events",
    response_model=SupportersWithdrawList,
    responses=make_responses(503),
)
async def supporters_withdraw(
        address: AddressFilterQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the supporters withdraw events, optionally filtered by an
    address (matched against msgSender, subaccount or receiver)."""
    db = await require_db()
    return await list_events(
        db, "event_Supporters_Withdraw", limit=limit, skip=skip,
        query_filter=address_in_any(address, ("msgSender", "subaccount", "receiver")),
        collation=CASE_INSENSITIVE_COLLATION if address else None)


@router.get(
    "/api/v1/omoc/supporters_withdraw_stake/",
    response_description="Returns the supporters withdraw stake events",
    response_model=SupportersWithdrawStakeList,
    responses=make_responses(503),
)
async def supporters_withdraw_stake(
        address: AddressFilterQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the supporters withdraw stake events, optionally filtered by an
    address (matched against user, subaccount or destination)."""
    db = await require_db()
    return await list_events(
        db, "event_Supporters_WithdrawStake", limit=limit, skip=skip,
        query_filter=address_in_any(address, ("user", "subaccount", "destination")),
        collation=CASE_INSENSITIVE_COLLATION if address else None)


# --- Voting Machine ---------------------------------------------------------------

@router.get(
    "/api/v1/omoc/voting_machine_pre_vote_event/",
    response_description="Returns the voting machine pre-vote events",
    response_model=VotingMachinePreVoteEventList,
    responses=make_responses(503),
)
async def voting_machine_pre_vote_event(limit: LimitQuery = 20, skip: SkipQuery = 0):
    """Returns the voting machine pre-vote events."""
    db = await require_db()
    return await list_events(
        db, "event_VotingMachine_PreVoteEvent", limit=limit, skip=skip)


@router.get(
    "/api/v1/omoc/voting_machine_vote_event/",
    response_description="Returns the voting machine vote events",
    response_model=VotingMachineVoteEventList,
    responses=make_responses(503),
)
async def voting_machine_vote_event(
        proposal: ProposalQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the voting machine vote events, optionally filtered by proposal
    address."""
    db = await require_db()
    return await list_events(
        db, "event_VotingMachine_VoteEvent", limit=limit, skip=skip,
        query_filter={"proposal": proposal} if proposal else None,
        collation=CASE_INSENSITIVE_COLLATION if proposal else None)


@router.get(
    "/api/v1/omoc/voting_machine_pre_vote_step_event/",
    response_description="Returns the voting machine pre-vote step events",
    response_model=VotingMachinePreVoteStepEventList,
    responses=make_responses(503),
)
async def voting_machine_pre_vote_step_event(
        proposal: ProposalQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the voting machine pre-vote step events, optionally filtered by
    proposal address."""
    db = await require_db()
    return await list_events(
        db, "event_VotingMachine_PreVoteStepEvent", limit=limit, skip=skip,
        query_filter={"proposal": proposal} if proposal else None,
        collation=CASE_INSENSITIVE_COLLATION if proposal else None)


@router.get(
    "/api/v1/omoc/voting_machine_vote_step_event/",
    response_description="Returns the voting machine vote step events",
    response_model=VotingMachineVoteStepEventList,
    responses=make_responses(503),
)
async def voting_machine_vote_step_event(limit: LimitQuery = 20, skip: SkipQuery = 0):
    """Returns the voting machine vote step events."""
    db = await require_db()
    return await list_events(
        db, "event_VotingMachine_VoteStepEvent", limit=limit, skip=skip)


@router.get(
    "/api/v1/omoc/voting_machine_accepted_step_event/",
    response_description="Returns the voting machine accepted step events",
    response_model=VotingMachineAcceptedStepEventList,
    responses=make_responses(503),
)
async def voting_machine_accepted_step_event(
        proposal: ProposalQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the voting machine accepted step events, optionally filtered by
    proposal address."""
    db = await require_db()
    return await list_events(
        db, "event_VotingMachine_AcceptedStepEvent", limit=limit, skip=skip,
        query_filter={"proposal": proposal} if proposal else None,
        collation=CASE_INSENSITIVE_COLLATION if proposal else None)


@router.get(
    "/api/v1/omoc/voting_machine_unregister_event/",
    response_description="Returns the voting machine unregister events",
    response_model=VotingMachineUnregisterEventList,
    responses=make_responses(503),
)
async def voting_machine_unregister_event(
        proposal: ProposalQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the voting machine unregister events, optionally filtered by
    proposal address."""
    db = await require_db()
    return await list_events(
        db, "event_VotingMachine_UnregisterEvent", limit=limit, skip=skip,
        query_filter={"proposal": proposal} if proposal else None,
        collation=CASE_INSENSITIVE_COLLATION if proposal else None)


# --- Oracle Manager -------------------------------------------------------------

@router.get(
    "/api/v1/omoc/oracle_manager_oracle_registered/",
    response_description="Returns the oracle manager oracle registered events",
    response_model=OracleManagerOracleRegisteredList,
    responses=make_responses(503),
)
async def oracle_manager_oracle_registered(
        caller: CallerQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the oracle manager oracle registered events, optionally filtered
    by caller address."""
    db = await require_db()
    return await list_events(
        db, "event_OracleManager_OracleRegistered", limit=limit, skip=skip,
        query_filter={"caller": caller} if caller else None,
        collation=CASE_INSENSITIVE_COLLATION if caller else None)


@router.get(
    "/api/v1/omoc/oracle_manager_oracle_stake_added/",
    response_description="Returns the oracle manager oracle stake added events",
    response_model=OracleManagerOracleStakeAddedList,
    responses=make_responses(503),
)
async def oracle_manager_oracle_stake_added(
        caller: CallerQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the oracle manager oracle stake added events, optionally filtered
    by caller address."""
    db = await require_db()
    return await list_events(
        db, "event_OracleManager_OracleStakeAdded", limit=limit, skip=skip,
        query_filter={"caller": caller} if caller else None,
        collation=CASE_INSENSITIVE_COLLATION if caller else None)


@router.get(
    "/api/v1/omoc/oracle_manager_oracle_subscribed/",
    response_description="Returns the oracle manager oracle subscribed events",
    response_model=OracleManagerOracleSubscribedList,
    responses=make_responses(503),
)
async def oracle_manager_oracle_subscribed(
        caller: CallerQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the oracle manager oracle subscribed events, optionally filtered
    by caller address."""
    db = await require_db()
    return await list_events(
        db, "event_OracleManager_OracleSubscribed", limit=limit, skip=skip,
        query_filter={"caller": caller} if caller else None,
        collation=CASE_INSENSITIVE_COLLATION if caller else None)


@router.get(
    "/api/v1/omoc/oracle_manager_oracle_unsubscribed/",
    response_description="Returns the oracle manager oracle unsubscribed events",
    response_model=OracleManagerOracleUnsubscribedList,
    responses=make_responses(503),
)
async def oracle_manager_oracle_unsubscribed(
        caller: CallerQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the oracle manager oracle unsubscribed events, optionally filtered
    by caller address."""
    db = await require_db()
    return await list_events(
        db, "event_OracleManager_OracleUnsubscribed", limit=limit, skip=skip,
        query_filter={"caller": caller} if caller else None,
        collation=CASE_INSENSITIVE_COLLATION if caller else None)


@router.get(
    "/api/v1/omoc/oracle_manager_oracle_removed/",
    response_description="Returns the oracle manager oracle removed events",
    response_model=OracleManagerOracleRemovedList,
    responses=make_responses(503),
)
async def oracle_manager_oracle_removed(
        caller: CallerQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the oracle manager oracle removed events, optionally filtered by
    caller address."""
    db = await require_db()
    return await list_events(
        db, "event_OracleManager_OracleRemoved", limit=limit, skip=skip,
        query_filter={"caller": caller} if caller else None,
        collation=CASE_INSENSITIVE_COLLATION if caller else None)


# --- CoinPairPrice (decentralized oracles) ------------------------------------

@router.get(
    "/api/v1/omoc/coin_pair_price_price_published/",
    response_description="Returns the CoinPairPrice price published events",
    response_model=CoinPairPricePricePublishedList,
    responses=make_responses(503),
)
async def coin_pair_price_price_published(
        coin_pair_address: CoinPairAddressQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the CoinPairPrice price published events, optionally filtered by
    the coin pair's contract address."""
    db = await require_db()
    return await list_events(
        db, "event_CoinPairPrice_PricePublished", limit=limit, skip=skip,
        query_filter={"contractAddress": coin_pair_address} if coin_pair_address else None,
        collation=CASE_INSENSITIVE_COLLATION if coin_pair_address else None)


@router.get(
    "/api/v1/omoc/coin_pair_price_emergency_price_published/",
    response_description="Returns the CoinPairPrice emergency price published events",
    response_model=CoinPairPriceEmergencyPricePublishedList,
    responses=make_responses(503),
)
async def coin_pair_price_emergency_price_published(
        coin_pair_address: CoinPairAddressQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the CoinPairPrice emergency price published events, optionally
    filtered by the coin pair's contract address."""
    db = await require_db()
    return await list_events(
        db, "event_CoinPairPrice_EmergencyPricePublished", limit=limit, skip=skip,
        query_filter={"contractAddress": coin_pair_address} if coin_pair_address else None,
        collation=CASE_INSENSITIVE_COLLATION if coin_pair_address else None)


@router.get(
    "/api/v1/omoc/coin_pair_price_forced_price_query_mode_set/",
    response_description="Returns the CoinPairPrice forced price query mode set events",
    response_model=CoinPairPriceForcedPriceQueryModeSetList,
    responses=make_responses(503),
)
async def coin_pair_price_forced_price_query_mode_set(
        coin_pair_address: CoinPairAddressQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the CoinPairPrice forced price query mode set events, optionally
    filtered by the coin pair's contract address."""
    db = await require_db()
    return await list_events(
        db, "event_CoinPairPrice_ForcedPriceQueryModeSet", limit=limit, skip=skip,
        query_filter={"contractAddress": coin_pair_address} if coin_pair_address else None,
        collation=CASE_INSENSITIVE_COLLATION if coin_pair_address else None)


@router.get(
    "/api/v1/omoc/coin_pair_price_oracle_reward_transfer/",
    response_description="Returns the CoinPairPrice oracle reward transfer events",
    response_model=CoinPairPriceOracleRewardTransferList,
    responses=make_responses(503),
)
async def coin_pair_price_oracle_reward_transfer(
        coin_pair_address: CoinPairAddressQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the CoinPairPrice oracle reward transfer events, optionally
    filtered by the coin pair's contract address."""
    db = await require_db()
    return await list_events(
        db, "event_CoinPairPrice_OracleRewardTransfer", limit=limit, skip=skip,
        query_filter={"contractAddress": coin_pair_address} if coin_pair_address else None,
        collation=CASE_INSENSITIVE_COLLATION if coin_pair_address else None)


@router.get(
    "/api/v1/omoc/coin_pair_price_new_round/",
    response_description="Returns the CoinPairPrice new round events",
    response_model=CoinPairPriceNewRoundList,
    responses=make_responses(503),
)
async def coin_pair_price_new_round(
        coin_pair_address: CoinPairAddressQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the CoinPairPrice new round events, optionally filtered by the
    coin pair's contract address."""
    db = await require_db()
    return await list_events(
        db, "event_CoinPairPrice_NewRound", limit=limit, skip=skip,
        query_filter={"contractAddress": coin_pair_address} if coin_pair_address else None,
        collation=CASE_INSENSITIVE_COLLATION if coin_pair_address else None)


@router.get(
    "/api/v1/omoc/coin_pair_price_oracle_auto_unsubscribed/",
    response_description="Returns the CoinPairPrice oracle auto unsubscribed events",
    response_model=CoinPairPriceOracleAutoUnsubscribedList,
    responses=make_responses(503),
)
async def coin_pair_price_oracle_auto_unsubscribed(
        coin_pair_address: CoinPairAddressQuery = None,
        limit: LimitQuery = 20,
        skip: SkipQuery = 0):
    """Returns the CoinPairPrice oracle auto unsubscribed events, optionally
    filtered by the coin pair's contract address."""
    db = await require_db()
    return await list_events(
        db, "event_CoinPairPrice_OracleAutoUnsubscribed", limit=limit, skip=skip,
        query_filter={"contractAddress": coin_pair_address} if coin_pair_address else None,
        collation=CASE_INSENSITIVE_COLLATION if coin_pair_address else None)
