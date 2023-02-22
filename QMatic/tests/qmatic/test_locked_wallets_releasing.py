import random

import pytest
from brownie import accounts
from brownie.network.account import Account
from brownie.network.contract import ProjectContract

from QMatic.adapters.contract_functions import (
    balance_of,
    development_push_date_of_contract,
    initializing_active_balance_locking_mechanism,
    mint,
    normal_transfer,
    remaining_blocked_tokens_at_now_of_address,
    transfer_with_locking,
    wallet_affected_by_locking_mechanism_state,
    approve_to_spend_tokens_by_agent,
    transfer_from_user_by_approved_agent,
    wallet_affected_by_locking_mechanism_state,
    linear_release_period_and_amount_of_address,
    linear_release_dividend_and_divisor_of_address,
    remaining_seconds_to_finishing_the_cliff_of_address,
    turn_development_mode_off,
)
from QMatic.schemas import Events, GeneralActiveBalanceLockingMechanismStructure
from QMatic.tests.constants import (
    DEFAULT_MINT_AMOUNT,
    DEPLOYER_ACCOUNT_INDEX,
    INVESTOR_ACCOUNT_INDEX,
    MAX_SUPPLY,
    MONTH_IN_DAYS,
    ONE_WEI,
    AGENT_ACCOUNT_INDEX,
    INVALID_TRANSFER_MORE_THAN_AVAILABLE_TOKEN_ERROR_MESSAGE,
    ONE_DAY_IN_SECONDS,
    INVALID_AMOUNT_OF_TRANSFER_WITH_LOCKING_MECHANISM_MESSAGE,
    LOCKING_MECHANISM_IS_NOT_ACTIVATED,
    WALLET_ALREADY_HAS_ACTIVATED_LOCKING_MECHANISM,
)


@pytest.mark.parametrize(
    "day_shifted",
    [
        i
        for i in range(
            0,
            366,
            30,
        )
    ],
)
def test_transfer_with_locking_mechanism_first_round(
    locking_mechanism_first_round_qmatic_contract: ProjectContract, day_shifted: int
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    cliff_duration_in_days: int = 3 * MONTH_IN_DAYS
    # sending token to investor
    transfer_events, revert_exception = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    assert revert_exception is None
    assert transfer_events is not None
    assert transfer_events.transfer is not None
    assert transfer_events.investment_with_locking_mechanism_scenario is not None

    investor_balance = balance_of(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=deployer_account,
    )
    assert (
        transfer_events.investment_with_locking_mechanism_scenario[
            0
        ].amount_of_invest_in_qmatic
        == investor_balance
    )

    # calculating amount of available transfer during the days
    total_locked_balance: int = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    assert (
        transfer_events.investment_with_locking_mechanism_scenario[
            0
        ].total_affected_tokens
        == total_locked_balance
    )
    investor_wallet_locking_state = wallet_affected_by_locking_mechanism_state(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=investor_account,
    )
    assert investor_wallet_locking_state.mechanism is not None
    locked_balance_after_success_transfer = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    development_push_date_of_contract(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        days=day_shifted,
        caller=deployer_account,
    )
    if day_shifted <= cliff_duration_in_days:
        assert total_locked_balance == locked_balance_after_success_transfer
        return
    days_after_cliff = day_shifted - cliff_duration_in_days

    remaining_blocked_amount = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    released_token = 0
    period_ticks = (
        days_after_cliff
        // investor_wallet_locking_state.mechanism.linear_release_period_in_days
    )
    period_ticks = period_ticks + 1
    released_token = (
        period_ticks * investor_wallet_locking_state.linear_release_tokens_per_period
    )
    remaining_blocked_amount_after_releasing = (
        locked_balance_after_success_transfer - released_token
    )

    normal_transfer(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=deployer_account.address,
        amount=released_token,
        caller=investor_account,
    )
    assert remaining_blocked_amount == remaining_blocked_amount_after_releasing
    if remaining_blocked_amount == 0:
        balance_of_investor_after_time_of_unlocking_everything = balance_of(
            qmatic_contract=locking_mechanism_first_round_qmatic_contract,
            account_address=investor_account.address,
            caller=deployer_account,
        )
        assert balance_of_investor_after_time_of_unlocking_everything == (
            transfer_events.investment_with_locking_mechanism_scenario[
                0
            ].amount_of_invest_in_qmatic
            - transfer_events.investment_with_locking_mechanism_scenario[
                0
            ].total_affected_tokens
        )


@pytest.mark.parametrize(
    "day_shifted",
    [
        i
        for i in range(
            0,
            366,
            30,
        )
    ],
)
def test_transfer_from_agent_with_locking_mechanism_first_round(
    locking_mechanism_first_round_qmatic_contract: ProjectContract, day_shifted: int
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    agent_account: Account = accounts[AGENT_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]

    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    cliff_duration_in_days: int = 3 * MONTH_IN_DAYS
    # sending token to investor
    transfer_events, revert_exception = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    assert revert_exception is None
    assert transfer_events is not None
    assert transfer_events.transfer is not None
    assert transfer_events.investment_with_locking_mechanism_scenario is not None

    investor_balance = balance_of(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=deployer_account,
    )
    assert (
        transfer_events.investment_with_locking_mechanism_scenario[
            0
        ].amount_of_invest_in_qmatic
        == investor_balance
    )
    (
        approve_agent_spending_money_event,
        approve_agent_reverted_message,
    ) = approve_to_spend_tokens_by_agent(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        spender_address=agent_account.address,
        amount_spend=amount_to_sell,
        caller=investor_account,
    )
    assert approve_agent_reverted_message is None
    assert approve_agent_spending_money_event is not None
    assert approve_agent_spending_money_event.approval is not None
    # calculating amount of available transfer during the days
    total_locked_balance: int = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    assert (
        transfer_events.investment_with_locking_mechanism_scenario[
            0
        ].total_affected_tokens
        == total_locked_balance
    )
    investor_wallet_locking_state = wallet_affected_by_locking_mechanism_state(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=investor_account,
    )
    assert investor_wallet_locking_state.mechanism is not None
    locked_balance_after_success_transfer = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    development_push_date_of_contract(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        days=day_shifted,
        caller=deployer_account,
    )
    if day_shifted <= cliff_duration_in_days:
        assert total_locked_balance == locked_balance_after_success_transfer
        return
    days_after_cliff = day_shifted - cliff_duration_in_days

    remaining_blocked_amount = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    released_token = 0
    period_ticks = (
        days_after_cliff
        // investor_wallet_locking_state.mechanism.linear_release_period_in_days
    )
    period_ticks = period_ticks + 1
    released_token = (
        period_ticks * investor_wallet_locking_state.linear_release_tokens_per_period
    )
    remaining_blocked_amount_after_releasing = (
        locked_balance_after_success_transfer - released_token
    )
    transfer_from_user_by_approved_agent(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        from_address=investor_account.address,
        to_address=deployer_account.address,
        amount=released_token,
        caller=agent_account,
    )
    assert remaining_blocked_amount == remaining_blocked_amount_after_releasing
    if remaining_blocked_amount == 0:
        balance_of_investor_after_time_of_unlocking_everything = balance_of(
            qmatic_contract=locking_mechanism_first_round_qmatic_contract,
            account_address=investor_account.address,
            caller=deployer_account,
        )
        assert balance_of_investor_after_time_of_unlocking_everything == (
            transfer_events.investment_with_locking_mechanism_scenario[
                0
            ].amount_of_invest_in_qmatic
            - transfer_events.investment_with_locking_mechanism_scenario[
                0
            ].total_affected_tokens
        )


@pytest.mark.parametrize(
    "day_shifted",
    [
        i
        for i in range(
            0,
            366,
            30,
        )
    ],
)
def test_invalid_transfer_more_than_available_balance_with_locking_mechanism_first_round(
    locking_mechanism_first_round_qmatic_contract: ProjectContract, day_shifted: int
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]

    amount_to_sell: int = DEFAULT_MINT_AMOUNT // 2
    amount_to_normal_transfer: int = DEFAULT_MINT_AMOUNT - amount_to_sell
    cliff_duration_in_days: int = 3 * MONTH_IN_DAYS
    # sending token to investor
    transfer_events, revert_exception = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    assert revert_exception is None
    assert transfer_events is not None
    assert transfer_events.transfer is not None
    assert transfer_events.investment_with_locking_mechanism_scenario is not None
    normal_transfer(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_normal_transfer,
        caller=deployer_account,
    )
    investor_balance = balance_of(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=deployer_account,
    )
    assert (
        transfer_events.investment_with_locking_mechanism_scenario[
            0
        ].amount_of_invest_in_qmatic
        == investor_balance - amount_to_normal_transfer
    )

    # calculating amount of available transfer during the days
    total_locked_balance: int = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    assert (
        transfer_events.investment_with_locking_mechanism_scenario[
            0
        ].total_affected_tokens
        == total_locked_balance
    )
    investor_wallet_locking_state = wallet_affected_by_locking_mechanism_state(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=investor_account,
    )
    assert investor_wallet_locking_state.mechanism is not None
    locked_balance_after_success_transfer = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    development_push_date_of_contract(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        days=day_shifted,
        caller=deployer_account,
    )
    remaining_blocked_amount = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=deployer_account,
    )
    if remaining_blocked_amount != 0:
        invalid_transfer_event, invalid_transfer_reverted_message = normal_transfer(
            qmatic_contract=locking_mechanism_first_round_qmatic_contract,
            to=deployer_account.address,
            amount=investor_balance,
            caller=investor_account,
        )
        assert invalid_transfer_event is None
        assert invalid_transfer_reverted_message is not None
        assert (
            invalid_transfer_reverted_message.msg
            == INVALID_TRANSFER_MORE_THAN_AVAILABLE_TOKEN_ERROR_MESSAGE
        )


def test_assigned_locking_mechanism_to_a_wallet(
    locking_mechanism_first_round_qmatic_contract: ProjectContract,
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    first_round_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )
    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    cliff_duration_in_days: int = 3 * MONTH_IN_DAYS
    # sending token to investor
    transfer_events, revert_exception = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    locking_mechanism_state = wallet_affected_by_locking_mechanism_state(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=investor_account,
    )
    assert (
        locking_mechanism_state.mechanism.linear_release_dividend
        == first_round_locking_mechanism.linear_release_dividend
    )
    assert (
        locking_mechanism_state.mechanism.linear_release_divisor
        == first_round_locking_mechanism.linear_release_divisor
    )
    linear_release_dividend_and_divisor = (
        linear_release_dividend_and_divisor_of_address(
            qmatic_contract=locking_mechanism_first_round_qmatic_contract,
            target_address=investor_account.address,
            caller=investor_account,
        )
    )
    linear_release_per_period = (
        (
            (
                amount_to_sell
                * (100 - first_round_locking_mechanism.releasing_tge_dividend_on_100)
            )
            // 100
        )
        * locking_mechanism_state.mechanism.linear_release_dividend
    ) // locking_mechanism_state.mechanism.linear_release_divisor
    releasing_period = linear_release_period_and_amount_of_address(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        target_address=investor_account.address,
        caller=investor_account,
    )
    assert (
        releasing_period.period_in_days
        == first_round_locking_mechanism.linear_release_period_in_days
    )
    assert releasing_period.release_amount_per_period == linear_release_per_period


@pytest.mark.parametrize(
    "day_shifted",
    [
        i
        for i in range(
            0,
            120,
            30,
        )
    ],
)
def test_remaining_seconds_to_end_of_cliff_development(
    locking_mechanism_first_round_qmatic_contract: ProjectContract, day_shifted: int
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    first_round_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )
    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    cliff_duration_in_days: int = 3 * MONTH_IN_DAYS
    # sending token to investor
    transfer_events, revert_exception = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    locking_mechanism_state = wallet_affected_by_locking_mechanism_state(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=investor_account,
    )
    expected_total_cliff_in_seconds = (
        first_round_locking_mechanism.cliff_duration_in_days * ONE_DAY_IN_SECONDS
    )
    actual_remaining_cliff_in_seconds = (
        remaining_seconds_to_finishing_the_cliff_of_address(
            qmatic_contract=locking_mechanism_first_round_qmatic_contract,
            target_address=investor_account.address,
            caller=investor_account,
        )
    )
    assert actual_remaining_cliff_in_seconds == expected_total_cliff_in_seconds
    development_push_date_of_contract(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        days=day_shifted,
        caller=deployer_account,
    )
    expected_total_cliff_in_seconds = expected_total_cliff_in_seconds - (
        day_shifted * ONE_DAY_IN_SECONDS
    )
    if expected_total_cliff_in_seconds <= 0:
        expected_total_cliff_in_seconds = 0

    actual_remaining_cliff_in_seconds = (
        remaining_seconds_to_finishing_the_cliff_of_address(
            qmatic_contract=locking_mechanism_first_round_qmatic_contract,
            target_address=investor_account.address,
            caller=investor_account,
        )
    )
    # tolerance of execution
    assert (expected_total_cliff_in_seconds - actual_remaining_cliff_in_seconds) >= 0
    assert (expected_total_cliff_in_seconds - actual_remaining_cliff_in_seconds) <= 2


def test_remaining_seconds_to_end_of_cliff_production(
    locking_mechanism_first_round_qmatic_contract: ProjectContract,
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    turn_development_mode_off(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        caller=deployer_account,
    )
    first_round_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )
    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    cliff_duration_in_days: int = 3 * MONTH_IN_DAYS
    # sending token to investor
    transfer_events, revert_exception = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    locking_mechanism_state = wallet_affected_by_locking_mechanism_state(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        account_address=investor_account.address,
        caller=investor_account,
    )
    expected_total_cliff_in_seconds = (
        first_round_locking_mechanism.cliff_duration_in_days * ONE_DAY_IN_SECONDS
    )
    actual_remaining_cliff_in_seconds = (
        remaining_seconds_to_finishing_the_cliff_of_address(
            qmatic_contract=locking_mechanism_first_round_qmatic_contract,
            target_address=investor_account.address,
            caller=investor_account,
        )
    )
    assert actual_remaining_cliff_in_seconds == expected_total_cliff_in_seconds


def test_transfer_with_locking_with_invalid_amount(
    locking_mechanism_first_round_qmatic_contract: ProjectContract,
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    event, reverted_message = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=1,
        caller=deployer_account,
    )
    assert event is None
    assert reverted_message is not None
    assert (
        reverted_message.msg
        == INVALID_AMOUNT_OF_TRANSFER_WITH_LOCKING_MECHANISM_MESSAGE
    )


def test_transfer_with_locking_with_no_active_locking_mechanism(
    qmatic_contract: ProjectContract,
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    event, reverted_message = transfer_with_locking(
        qmatic_contract=qmatic_contract,
        to=investor_account.address,
        amount=1_000_000,
        caller=deployer_account,
    )
    assert event is None
    assert reverted_message is not None
    assert reverted_message.msg == LOCKING_MECHANISM_IS_NOT_ACTIVATED


def test_transfer_with_locking_to_the_wallet_who_already_has_active_locking(
    locking_mechanism_first_round_qmatic_contract: ProjectContract,
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=1_000_000,
        caller=deployer_account,
    )
    event, reverted_message = transfer_with_locking(
        qmatic_contract=locking_mechanism_first_round_qmatic_contract,
        to=investor_account.address,
        amount=1_000_000,
        caller=deployer_account,
    )
    assert event is None
    assert reverted_message is not None
    assert reverted_message.msg == WALLET_ALREADY_HAS_ACTIVATED_LOCKING_MECHANISM


@pytest.mark.parametrize(
    "day_shifted",
    [
        i
        for i in range(
            0,
            42,
            7,
        )
    ],
)
def test_remaining_locked_tokens_with_just_cliff_locking_mechanism(
    qmatic_contract: ProjectContract, day_shifted: int
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    # sending token to investor
    mint(
        qmatic_contract=qmatic_contract,
        to=deployer_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    entries = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=1 * MONTH_IN_DAYS,
        linear_release_period_in_days=0,
        linear_release_dividend=0,
        linear_release_divisor=0,
        releasing_tge_dividend_on_100=0,
    )
    initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract, entries=entries, caller=deployer_account
    )
    transfer_with_locking(
        qmatic_contract=qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    development_push_date_of_contract(
        qmatic_contract=qmatic_contract, days=day_shifted, caller=deployer_account
    )
    expected_remaining_tokens = 0
    if day_shifted <= (1 * MONTH_IN_DAYS):
        expected_remaining_tokens = amount_to_sell

    actual_remaining_blocked_tokens = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=qmatic_contract,
        target_address=investor_account.address,
        caller=investor_account,
    )
    print("expected_remaining_tokens", expected_remaining_tokens)
    print("actual_remaining_blocked_tokens", actual_remaining_blocked_tokens)

    assert actual_remaining_blocked_tokens == expected_remaining_tokens


@pytest.mark.parametrize(
    "day_shifted",
    [
        i
        for i in range(
            0,
            150,
            10,
        )
    ],
)
def test_remaining_locked_tokens_with_just_linear_releasing_locking_mechanism(
    qmatic_contract: ProjectContract, day_shifted: int
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    # sending token to investor
    mint(
        qmatic_contract=qmatic_contract,
        to=deployer_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    entries = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=0,
        linear_release_period_in_days=10,
        linear_release_dividend=20,
        linear_release_divisor=100,
        releasing_tge_dividend_on_100=0,
    )
    initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract, entries=entries, caller=deployer_account
    )
    transfer_with_locking(
        qmatic_contract=qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    development_push_date_of_contract(
        qmatic_contract=qmatic_contract, days=day_shifted, caller=deployer_account
    )
    expected_remaining_blocked_tokens = amount_to_sell - (
        ((day_shifted // 10) + 1)
        * (
            (amount_to_sell * entries.linear_release_dividend)
            // entries.linear_release_divisor
        )
    )
    if expected_remaining_blocked_tokens <= 0:
        expected_remaining_blocked_tokens = 0

    actual_remaining_blocked_tokens = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=qmatic_contract,
        target_address=investor_account.address,
        caller=investor_account,
    )
    print("expected_remaining_blocked_tokens", expected_remaining_blocked_tokens)
    print("actual_remaining_blocked_tokens", actual_remaining_blocked_tokens)

    assert actual_remaining_blocked_tokens == expected_remaining_blocked_tokens


def test_remaining_locked_tokens_with_just_linear_releasing_locking_mechanism_on_production(
    production_qmatic_contract: ProjectContract,
) -> None:
    investor_account: Account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account: Account = accounts[DEPLOYER_ACCOUNT_INDEX]
    amount_to_sell: int = DEFAULT_MINT_AMOUNT
    # sending token to investor
    mint(
        qmatic_contract=production_qmatic_contract,
        to=deployer_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    entries = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=0,
        linear_release_period_in_days=10,
        linear_release_dividend=20,
        linear_release_divisor=100,
        releasing_tge_dividend_on_100=0,
    )
    initializing_active_balance_locking_mechanism(
        qmatic_contract=production_qmatic_contract,
        entries=entries,
        caller=deployer_account,
    )
    transfer_with_locking(
        qmatic_contract=production_qmatic_contract,
        to=investor_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    expected_remaining_blocked_tokens = amount_to_sell - (
        (amount_to_sell * entries.linear_release_dividend)
        // entries.linear_release_divisor
    )

    if expected_remaining_blocked_tokens <= 0:
        expected_remaining_blocked_tokens = 0

    actual_remaining_blocked_tokens = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=production_qmatic_contract,
        target_address=investor_account.address,
        caller=investor_account,
    )
    print("expected_remaining_blocked_tokens", expected_remaining_blocked_tokens)
    print("actual_remaining_blocked_tokens", actual_remaining_blocked_tokens)

    assert actual_remaining_blocked_tokens == expected_remaining_blocked_tokens
