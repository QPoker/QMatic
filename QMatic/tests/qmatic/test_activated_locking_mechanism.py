import random

import pytest
from brownie import ZERO_ADDRESS, accounts
from brownie.network.contract import ProjectContract

from QMatic.adapters import (
    active_balance_locking_mechanism,
    balance_of,
    contract_locking_for_upgrade,
    initializing_active_balance_locking_mechanism,
    mint,
    normal_transfer,
    remaining_blocked_tokens_at_now_of_address,
    transfer_with_locking,
    deactivate_balance_locking_mechanism,
    turn_development_mode_off,
)
from QMatic.schemas import (
    Events,
    GeneralActiveBalanceLockingMechanismStructure,
    RevertedMessage,
)
from QMatic.tests.constants import (
    INVESTOR_ACCOUNT_INDEX,
    DEPLOYER_ACCOUNT_INDEX,
    INVALID_LINEAR_RELEASE_PERIOD_IN_DAYS,
    LINEAR_RELEASED_DIVISOR_SUPPORTS,
    MAX_SUPPLY,
    MONTH_IN_DAYS,
    ONE_WEI,
    INVALID_TRANSFER_MORE_THAN_AVAILABLE_TOKEN_ERROR_MESSAGE,
    INVALID_LINEAR_RELEASE_DIVISOR_MESSAGE,
    MEANINGLESS_LOCKING_MECHANISM_ERROR_MESSAGE,
    INVALID_LINEAR_RELEASE_PERIOD_IN_DAYS_MESSAGE,
    INT_DEFAULT_VALUE,
)


SOME_RANDOM_ACCOUNT_TO_TRANSFER_TOKENS = random.randint(1, 9)

VALID_LOCKING_MECHANISM_FIRST_ROUND = GeneralActiveBalanceLockingMechanismStructure(
    cliff_duration_in_days=3 * MONTH_IN_DAYS,
    linear_release_period_in_days=1 * MONTH_IN_DAYS,
    linear_release_dividend=1,
    linear_release_divisor=10,
    releasing_tge_dividend_on_100=15,
)


def assert_has_reverted_message(
    log: Events | None, revert_exception: RevertedMessage | None, msg: str
) -> None:
    assert log is None
    assert revert_exception is not None
    assert revert_exception.msg == msg


def test_set_and_delete_a_valid_locking_mechanism(
    qmatic_contract: ProjectContract,
) -> None:
    mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )

    init_events, revert_exception = initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=mechanism,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )

    assert revert_exception is None
    assert init_events is not None
    assert init_events.balance_locking_mechanism_update_log is not None
    assert (
        init_events.balance_locking_mechanism_update_log[0].cliff_duration_in_days,
        init_events.balance_locking_mechanism_update_log[
            0
        ].linear_release_period_in_days,
        init_events.balance_locking_mechanism_update_log[0].linear_release_dividend,
        init_events.balance_locking_mechanism_update_log[0].linear_release_divisor,
        init_events.balance_locking_mechanism_update_log[
            0
        ].releasing_tge__dividend_on_100,
    ) == (
        mechanism.cliff_duration_in_days,
        mechanism.linear_release_period_in_days,
        mechanism.linear_release_dividend,
        mechanism.linear_release_divisor,
        mechanism.releasing_tge_dividend_on_100,
    )
    active_mechanism = active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    assert active_mechanism == mechanism
    (
        deactivate_event,
        deactivate_revert_exception,
    ) = deactivate_balance_locking_mechanism(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    assert deactivate_event is not None
    assert deactivate_event.balance_locking_mechanism_update_log is not None
    assert deactivate_revert_exception is None
    deactivated_mechanism = active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    assert deactivated_mechanism == GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=INT_DEFAULT_VALUE,
        linear_release_period_in_days=INT_DEFAULT_VALUE,
        linear_release_dividend=INT_DEFAULT_VALUE,
        linear_release_divisor=INT_DEFAULT_VALUE,
        releasing_tge_dividend_on_100=INT_DEFAULT_VALUE,
    )
    assert (
        init_events.balance_locking_mechanism_update_log[0].cliff_duration_in_days,
        init_events.balance_locking_mechanism_update_log[
            0
        ].linear_release_period_in_days,
        init_events.balance_locking_mechanism_update_log[0].linear_release_dividend,
        init_events.balance_locking_mechanism_update_log[0].linear_release_divisor,
        init_events.balance_locking_mechanism_update_log[
            0
        ].releasing_tge__dividend_on_100,
    ) == (
        deactivate_event.balance_locking_mechanism_update_log[0].cliff_duration_in_days,
        deactivate_event.balance_locking_mechanism_update_log[
            0
        ].linear_release_period_in_days,
        deactivate_event.balance_locking_mechanism_update_log[
            0
        ].linear_release_dividend,
        deactivate_event.balance_locking_mechanism_update_log[0].linear_release_divisor,
        deactivate_event.balance_locking_mechanism_update_log[
            0
        ].releasing_tge__dividend_on_100,
    )
    assert (
        init_events.balance_locking_mechanism_update_log[0].is_active
        != deactivate_event.balance_locking_mechanism_update_log[
            0
        ].releasing_tge__dividend_on_100
    )


@pytest.mark.parametrize(
    "linear_release_divisor,linear_release_dividend",
    [(10, 11), (100, 101), (1_000, 1_001), (10_000, 10_001), (100_000, 100_001)],
)
def test_set_a_not_valid_locking_mechanism_error_on_linear_release_dividend(
    qmatic_contract: ProjectContract,
    linear_release_divisor: int,
    linear_release_dividend: int,
) -> None:
    invalid_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )
    invalid_locking_mechanism.linear_release_divisor = linear_release_divisor
    invalid_locking_mechanism.linear_release_dividend = linear_release_dividend
    log, revert_exception = initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=invalid_locking_mechanism,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert_has_reverted_message(
        log, revert_exception, INVALID_LINEAR_RELEASE_DIVISOR_MESSAGE
    )
    print("linear_release_divisor", linear_release_divisor)
    print("linear_release_dividend", linear_release_dividend)


@pytest.mark.parametrize(
    "linear_release_divisor",
    [11, 101, 1_001, 10_001, 100_001],
)
def test_set_a_not_valid_locking_mechanism_error_on_linear_release_divisor(
    qmatic_contract: ProjectContract,
    linear_release_divisor: int,
) -> None:
    invalid_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )
    invalid_locking_mechanism.linear_release_divisor = linear_release_divisor
    log, revert_exception = initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=invalid_locking_mechanism,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert_has_reverted_message(
        log, revert_exception, INVALID_LINEAR_RELEASE_DIVISOR_MESSAGE
    )


@pytest.mark.parametrize(
    "linear_release_divisor",
    LINEAR_RELEASED_DIVISOR_SUPPORTS,
)
def test_set_a_not_valid_locking_mechanism_error_on_linear_release_period_in_days(
    qmatic_contract: ProjectContract,
    linear_release_divisor: int,
) -> None:
    invalid_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )
    invalid_locking_mechanism.linear_release_divisor = linear_release_divisor
    # just to make 'linear_release_dividend' more than the linear_release_divisor.
    invalid_locking_mechanism.linear_release_dividend = (
        invalid_locking_mechanism.linear_release_divisor
        - random.randint(1, linear_release_divisor - 1)
    )
    invalid_locking_mechanism.linear_release_period_in_days = (
        INVALID_LINEAR_RELEASE_PERIOD_IN_DAYS
    )
    log, revert_exception = initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=invalid_locking_mechanism,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert_has_reverted_message(
        log, revert_exception, INVALID_LINEAR_RELEASE_PERIOD_IN_DAYS_MESSAGE
    )


@pytest.mark.parametrize(
    "linear_release_divisor",
    LINEAR_RELEASED_DIVISOR_SUPPORTS,
)
def test_set_a_meaningless_locking_mechanism(
    qmatic_contract: ProjectContract,
    linear_release_divisor: int,
) -> None:
    invalid_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=1 * MONTH_IN_DAYS,
        linear_release_dividend=1,
        linear_release_divisor=10,
        releasing_tge_dividend_on_100=15,
    )
    invalid_locking_mechanism.linear_release_dividend = 0
    invalid_locking_mechanism.cliff_duration_in_days = 0

    log, revert_exception = initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=invalid_locking_mechanism,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert_has_reverted_message(
        log, revert_exception, MEANINGLESS_LOCKING_MECHANISM_ERROR_MESSAGE
    )


def test_set_just_cliff_locking_mechanism(
    qmatic_contract: ProjectContract,
) -> None:
    valid_locking_mechanism = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=3 * MONTH_IN_DAYS,
        linear_release_period_in_days=0,
        linear_release_dividend=0,
        linear_release_divisor=0,
        releasing_tge_dividend_on_100=15,
    )
    log, revert_exception = initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=valid_locking_mechanism,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is None
    assert log is not None
    assert log.balance_locking_mechanism_update_log is not None


@pytest.mark.parametrize(
    "amount_to_sell",
    [r * random.randint(1, 700_000_000) * ONE_WEI for r in range(1, 5)],
)
def test_transfer_to_investor_with_activated_locking_mechanism(
    qmatic_contract: ProjectContract,
    amount_to_sell: int,
) -> None:
    investor_account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account = accounts[DEPLOYER_ACCOUNT_INDEX]

    # minting token
    mint(
        qmatic_contract=qmatic_contract,
        to=deployer_account.address,
        amount=amount_to_sell,
        caller=deployer_account,
    )
    # activating locking mechanism
    initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=VALID_LOCKING_MECHANISM_FIRST_ROUND,
        caller=deployer_account,
    )
    amount_to_buy = amount_to_sell
    # (transfer_log, investment_locking_log, revert_exception,) = transfer_with_locking(
    events, revert_exception = transfer_with_locking(
        qmatic_contract=qmatic_contract,
        to=investor_account.address,
        amount=amount_to_buy,
        caller=deployer_account,
    )
    assert revert_exception is None
    assert events is not None
    assert events.investment_with_locking_mechanism_scenario is not None
    assert events.transfer is not None

    assert events.transfer[0].from_address == deployer_account.address
    assert events.transfer[0].to_address == investor_account.address
    assert events.transfer[0].value == amount_to_buy
    # checking investment locking

    assert (
        events.investment_with_locking_mechanism_scenario[0].account_address
        == investor_account.address
    )
    total_affected_tokens: int = amount_to_buy - (
        (
            amount_to_buy
            * VALID_LOCKING_MECHANISM_FIRST_ROUND.releasing_tge_dividend_on_100
        )
        // 100
    )

    assert (
        events.investment_with_locking_mechanism_scenario[0].total_affected_tokens
        == total_affected_tokens
    )
    linear_release_tokens_per_period: int = (
        VALID_LOCKING_MECHANISM_FIRST_ROUND.linear_release_dividend
        * total_affected_tokens
    ) // VALID_LOCKING_MECHANISM_FIRST_ROUND.linear_release_divisor
    assert (
        events.investment_with_locking_mechanism_scenario[
            0
        ].linear_release_tokens_per_period
        == linear_release_tokens_per_period
    )
    assert (
        events.investment_with_locking_mechanism_scenario[0].amount_of_invest_in_qmatic
        == amount_to_buy
    )


@pytest.mark.parametrize(
    "amount_to_buy",
    [random.randint(1, 700_000_000) * ONE_WEI],
)
def test_transfer_invalid_amount_from_active_locking_mechanism_affected_wallet_development(
    qmatic_contract: ProjectContract, amount_to_buy: int
) -> None:
    investor_account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account = accounts[DEPLOYER_ACCOUNT_INDEX]

    # minting token
    mint(
        qmatic_contract=qmatic_contract,
        to=deployer_account.address,
        amount=amount_to_buy,
        caller=deployer_account,
    )
    # activating locking mechanism
    initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=VALID_LOCKING_MECHANISM_FIRST_ROUND,
        caller=deployer_account,
    )
    transfer_with_locking(
        qmatic_contract=qmatic_contract,
        to=investor_account.address,
        amount=amount_to_buy,
        caller=deployer_account,
    )
    locked_amount = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=qmatic_contract,
        target_address=investor_account.address,
        caller=investor_account,
    )
    assert locked_amount != 0
    balance_of_account = balance_of(
        qmatic_contract=qmatic_contract,
        account_address=investor_account.address,
        caller=investor_account,
    )
    released_tokens_calculated_by_contract = balance_of_account - locked_amount

    released_token_we_expect = (
        VALID_LOCKING_MECHANISM_FIRST_ROUND.releasing_tge_dividend_on_100
        * balance_of_account
    ) // 100
    assert released_tokens_calculated_by_contract == released_token_we_expect
    amount_to_transfer = random.randint(
        released_tokens_calculated_by_contract + 1, balance_of_account
    )
    transfer_log, revert_exception = normal_transfer(
        qmatic_contract=qmatic_contract,
        to=deployer_account.address,
        amount=amount_to_transfer,
        caller=investor_account,
    )
    assert_has_reverted_message(
        transfer_log,
        revert_exception,
        INVALID_TRANSFER_MORE_THAN_AVAILABLE_TOKEN_ERROR_MESSAGE,
    )


@pytest.mark.parametrize(
    "amount_to_buy",
    [random.randint(1, 700_000_000) * ONE_WEI],
)
def test_transfer_invalid_amount_from_active_locking_mechanism_affected_wallet_production(
    qmatic_contract: ProjectContract, amount_to_buy: int
) -> None:
    investor_account = accounts[INVESTOR_ACCOUNT_INDEX]
    deployer_account = accounts[DEPLOYER_ACCOUNT_INDEX]
    turn_development_mode_off(qmatic_contract=qmatic_contract, caller=deployer_account)
    expected_locked_tokens = amount_to_buy - (
        (
            amount_to_buy
            * VALID_LOCKING_MECHANISM_FIRST_ROUND.releasing_tge_dividend_on_100
        )
        // 100
    )
    # minting token
    mint(
        qmatic_contract=qmatic_contract,
        to=deployer_account.address,
        amount=amount_to_buy,
        caller=deployer_account,
    )
    # activating locking mechanism
    initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=VALID_LOCKING_MECHANISM_FIRST_ROUND,
        caller=deployer_account,
    )
    transfer_with_locking(
        qmatic_contract=qmatic_contract,
        to=investor_account.address,
        amount=amount_to_buy,
        caller=deployer_account,
    )
    locked_amount = remaining_blocked_tokens_at_now_of_address(
        qmatic_contract=qmatic_contract,
        target_address=investor_account.address,
        caller=investor_account,
    )
    assert locked_amount == expected_locked_tokens
