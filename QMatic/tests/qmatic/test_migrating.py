from brownie import accounts, ZERO_ADDRESS
from brownie.network.contract import ProjectContract

from QMatic.tests.constants import (
    QMATIC_CONTRACT_NAME_BEFORE_MIGRATING,
    QMATIC_CONTRACT_NAME_AFTER_MIGRATING,
    DEPLOYER_ACCOUNT_INDEX,
    STRING_DEFAULT,
)
from QMatic.adapters import name, contract_locking_for_upgrade

QPOKER_MERGING_URL = f"https://QPker.io/contracts/{ZERO_ADDRESS}"


def test_lock_contract_for_merging(qmatic_contract: ProjectContract) -> None:
    deployer_account = accounts[DEPLOYER_ACCOUNT_INDEX]
    events, revert_exception = contract_locking_for_upgrade(
        qmatic_contract=qmatic_contract,
        new_qmatic_address=ZERO_ADDRESS,
        report_url=QPOKER_MERGING_URL,
        caller=deployer_account,
    )
    assert revert_exception is None
    assert events is not None
    assert events.contract_upgrade is not None
    assert (
        events.contract_upgrade[0].new_token_contract_address,
        events.contract_upgrade[0].event_report_url,
    ) == (
        ZERO_ADDRESS,
        QPOKER_MERGING_URL,
    )
    assert events.contract_upgrade[0].upgrade_date > 0


def test_name_of_the_contract_before_migrating(
    qmatic_contract: ProjectContract,
) -> None:
    contract_name = name(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    assert contract_name == QMATIC_CONTRACT_NAME_BEFORE_MIGRATING


def test_name_of_the_contract_after_migrating(qmatic_contract: ProjectContract) -> None:
    contract_locking_for_upgrade(
        new_qmatic_address=ZERO_ADDRESS,
        report_url=STRING_DEFAULT,
        qmatic_contract=qmatic_contract,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    contract_name = name(
        qmatic_contract=qmatic_contract, caller=accounts[DEPLOYER_ACCOUNT_INDEX]
    )
    assert contract_name == QMATIC_CONTRACT_NAME_AFTER_MIGRATING
