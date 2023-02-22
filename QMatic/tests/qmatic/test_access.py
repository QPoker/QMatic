from brownie import ZERO_ADDRESS, accounts
from brownie.network.contract import ProjectContract

from QMatic.adapters import (
    contract_locking_for_upgrade,
    deactivate_balance_locking_mechanism,
    development_push_date_of_contract,
    development_status,
    initializing_active_balance_locking_mechanism,
    mint,
    transfer_with_locking,
    turn_development_mode_off,
)
from QMatic.schemas import (
    GeneralActiveBalanceLockingMechanismStructure,
    RevertedMessage,
)
from QMatic.tests.constants import (
    DEPLOYER_ACCOUNT_INDEX,
    INT_DEFAULT_VALUE,
    NONE_DEPLOYER_ACCOUNT_INDEX,
    NOT_DEVELOPMENT_ERROR_MESSAGE,
    NOT_OWNER_ERROR_MESSAGE,
    STRING_DEFAULT,
)


def test_not_owner_initializing_active_balance_locking_mechanism(
    qmatic_contract: ProjectContract,
) -> None:
    entries = GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=INT_DEFAULT_VALUE,
        linear_release_period_in_days=INT_DEFAULT_VALUE,
        linear_release_dividend=INT_DEFAULT_VALUE,
        linear_release_divisor=INT_DEFAULT_VALUE,
        releasing_tge_dividend_on_100=INT_DEFAULT_VALUE,
    )
    events, revert_exception = initializing_active_balance_locking_mechanism(
        qmatic_contract=qmatic_contract,
        entries=entries,
        caller=accounts[NONE_DEPLOYER_ACCOUNT_INDEX],
    )
    assert events == None
    assert revert_exception is not None
    assert revert_exception.msg == NOT_OWNER_ERROR_MESSAGE


def test_not_owner_deactivate_balance_locking_mechanism(
    qmatic_contract: ProjectContract,
) -> None:
    events, revert_exception = deactivate_balance_locking_mechanism(
        qmatic_contract=qmatic_contract, caller=accounts[NONE_DEPLOYER_ACCOUNT_INDEX]
    )
    assert events == None
    assert revert_exception is not None
    assert revert_exception.msg == NOT_OWNER_ERROR_MESSAGE


def test_not_owner_contract_locking_for_upgrade(
    qmatic_contract: ProjectContract,
) -> None:
    events, revert_exception = contract_locking_for_upgrade(
        new_qmatic_address=ZERO_ADDRESS,
        report_url=STRING_DEFAULT,
        qmatic_contract=qmatic_contract,
        caller=accounts[NONE_DEPLOYER_ACCOUNT_INDEX],
    )
    assert events == None
    assert revert_exception is not None
    assert revert_exception.msg == NOT_OWNER_ERROR_MESSAGE


def test_not_owner_mint(qmatic_contract: ProjectContract) -> None:
    events, revert_exception = mint(
        to=ZERO_ADDRESS,
        amount=INT_DEFAULT_VALUE,
        qmatic_contract=qmatic_contract,
        caller=accounts[NONE_DEPLOYER_ACCOUNT_INDEX],
    )
    assert events == None
    assert revert_exception is not None
    assert revert_exception.msg == NOT_OWNER_ERROR_MESSAGE


def test_not_owner_development_push_date_of_contract(
    qmatic_contract: ProjectContract,
) -> None:
    revert_exception = development_push_date_of_contract(
        days=INT_DEFAULT_VALUE,
        qmatic_contract=qmatic_contract,
        caller=accounts[NONE_DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is not None
    assert revert_exception.msg == NOT_OWNER_ERROR_MESSAGE


def test_not_owner_turn_developer_mode_off(qmatic_contract: ProjectContract) -> None:
    revert_exception = turn_development_mode_off(
        qmatic_contract=qmatic_contract,
        caller=accounts[NONE_DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is not None
    assert revert_exception.msg == NOT_OWNER_ERROR_MESSAGE


def test_turn_developer_mode_off(qmatic_contract: ProjectContract) -> None:
    turn_development_mode_off(
        qmatic_contract=qmatic_contract,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    is_developer_mode = development_status(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    assert is_developer_mode == False
    revert_exception = turn_development_mode_off(
        qmatic_contract=qmatic_contract,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is not None
    assert revert_exception.msg == NOT_DEVELOPMENT_ERROR_MESSAGE


def test_turn_developer_mode_off_when_its_already_in_production(
    production_qmatic_contract: ProjectContract,
) -> None:
    revert_exception = turn_development_mode_off(
        qmatic_contract=production_qmatic_contract,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is not None
    assert revert_exception.msg == NOT_DEVELOPMENT_ERROR_MESSAGE


def test_not_owner_transfer_without_locking(qmatic_contract: ProjectContract) -> None:
    events, revert_exception = transfer_with_locking(
        to=ZERO_ADDRESS,
        amount=INT_DEFAULT_VALUE,
        qmatic_contract=qmatic_contract,
        caller=accounts[NONE_DEPLOYER_ACCOUNT_INDEX],
    )
    assert events is None
    assert revert_exception is not None
    assert revert_exception.msg == NOT_OWNER_ERROR_MESSAGE


def test_production_mode_push_date_of_contract(
    qmatic_contract: ProjectContract,
) -> None:
    turn_development_mode_off(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    revert_exception = development_push_date_of_contract(
        qmatic_contract=qmatic_contract,
        days=12,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is not None
    assert revert_exception.msg == NOT_DEVELOPMENT_ERROR_MESSAGE


def test_production_turns_development_mode_off(
    qmatic_contract: ProjectContract,
) -> None:
    revert_exception = turn_development_mode_off(
        qmatic_contract=qmatic_contract,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is None
    revert_exception = turn_development_mode_off(
        qmatic_contract=qmatic_contract,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is not None
    assert revert_exception.msg == NOT_DEVELOPMENT_ERROR_MESSAGE
    current_development_status = development_status(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    assert current_development_status == False
