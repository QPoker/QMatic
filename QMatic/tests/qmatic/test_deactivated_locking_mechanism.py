import random
from typing import Union

import pytest
from brownie import ZERO_ADDRESS, accounts
from brownie.network.contract import ProjectContract

# VALID_LOCKING_MECHANISM_FIRST_ROUND,
# VALID_LOCKING_MECHANISM_SECOND_ROUND,
# VALID_LOCKING_MECHANISM_THIRD_ROUND,
# INVALID_LOCKING_MECHANISM_BASE_VALUE,
from QMatic.adapters.contract_functions import balance_of, mint, normal_transfer
from QMatic.schemas import (
    Events,
    GeneralActiveBalanceLockingMechanismStructure,
    RevertedMessage,
)
from QMatic.tests.constants import (
    DEFAULT_MINT_AMOUNT,
    DEPLOYER_ACCOUNT_INDEX,
    EMPTY_BALANCE_AMOUNT,
    INVALID_LINEAR_RELEASE_PERIOD_IN_DAYS,
    LINEAR_RELEASED_DIVISOR_SUPPORTS,
    MAX_SUPPLY,
    MINIMUM_AMOUNT_TO_SELL,
    MINT_MORE_THAN_MAX_SUPPLY_ERROR_MESSAGE,
    ONE_WEI,
    STRING_DEFAULT,
    MINIMUM_AMOUNT_TO_SELL,
    INVESTOR_ACCOUNT_INDEX,
    ERC20_INVALID_TRANSFER_MORE_THAN_BALANCE,
)


def test_transfer_more_than_balance(qmatic_contract: ProjectContract) -> None:
    deployer = accounts[DEPLOYER_ACCOUNT_INDEX]
    not_deployer_account = accounts[INVESTOR_ACCOUNT_INDEX]
    mint(
        qmatic_contract=qmatic_contract,
        to=deployer.address,
        amount=MINIMUM_AMOUNT_TO_SELL,
        caller=deployer,
    )
    log, reverted_message = normal_transfer(
        qmatic_contract=qmatic_contract,
        to=not_deployer_account.address,
        amount=MINIMUM_AMOUNT_TO_SELL * 2,
        caller=deployer,
    )
    assert reverted_message.msg == ERC20_INVALID_TRANSFER_MORE_THAN_BALANCE


@pytest.mark.parametrize(
    "mint_amount",
    [MAX_SUPPLY, 0, DEFAULT_MINT_AMOUNT],
)
def test_mint_lower_than_max_supply(
    qmatic_contract: ProjectContract, mint_amount: int
) -> None:
    mint_to_address = accounts[DEPLOYER_ACCOUNT_INDEX].address
    events, revert_exception = mint(
        qmatic_contract=qmatic_contract,
        to=mint_to_address,
        amount=mint_amount,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert revert_exception is None
    assert events is not None
    assert events.transfer is not None
    assert events.transfer[0].from_address == ZERO_ADDRESS
    assert events.transfer[0].to_address == mint_to_address
    assert events.transfer[0].value == mint_amount


def test_mint_more_than_max_supply(qmatic_contract: ProjectContract) -> None:
    amount_to_mint = MAX_SUPPLY + random.randint(1, MAX_SUPPLY)
    mint_to_address = accounts[DEPLOYER_ACCOUNT_INDEX].address
    events, revert_exception = mint(
        qmatic_contract=qmatic_contract,
        to=mint_to_address,
        amount=amount_to_mint,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert events is None
    assert revert_exception is not None
    assert revert_exception.msg == MINT_MORE_THAN_MAX_SUPPLY_ERROR_MESSAGE


@pytest.mark.parametrize(
    "destination_account_index",
    [1, 2],
)
@pytest.mark.parametrize(
    "safe_transfer_share_on_100",
    [50],
)
def test_safe_transfer_from_minter_to_user(
    qmatic_contract: ProjectContract,
    destination_account_index: int,
    safe_transfer_share_on_100: int,
) -> None:
    mint_to_address = accounts[DEPLOYER_ACCOUNT_INDEX].address
    mint_amount = random.randint(ONE_WEI, MAX_SUPPLY)

    mint(
        qmatic_contract=qmatic_contract,
        to=mint_to_address,
        amount=mint_amount,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    balance_of_minter = balance_of(
        qmatic_contract=qmatic_contract,
        account_address=mint_to_address,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert balance_of_minter == mint_amount
    amount_to_transfer = (balance_of_minter * safe_transfer_share_on_100) // 100
    events, revert_exception = normal_transfer(
        qmatic_contract=qmatic_contract,
        to=accounts[destination_account_index],
        amount=amount_to_transfer,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert events is not None
    assert revert_exception is None

    receiver_balance_after_transfer = balance_of(
        qmatic_contract=qmatic_contract,
        account_address=accounts[destination_account_index].address,
        caller=accounts[destination_account_index],
    )
    assert receiver_balance_after_transfer == amount_to_transfer
    balance_of_minter_after_transaction = balance_of(
        qmatic_contract=qmatic_contract,
        account_address=accounts[DEPLOYER_ACCOUNT_INDEX].address,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    assert balance_of_minter_after_transaction == (
        balance_of_minter - amount_to_transfer
    )
