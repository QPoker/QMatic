from typing import Generator

import pytest
from brownie import QMatic, accounts, chain
from brownie.network.contract import ProjectContract

from QMatic.adapters import initializing_active_balance_locking_mechanism, mint
from QMatic.schemas import GeneralActiveBalanceLockingMechanismStructure

from .constants import DEFAULT_MINT_AMOUNT, DEPLOYER_ACCOUNT_INDEX, MONTH_IN_DAYS


@pytest.fixture
def qmatic_contract() -> Generator[ProjectContract, None, None]:
    yield QMatic.deploy(True, {"from": accounts[DEPLOYER_ACCOUNT_INDEX]})
    chain.reset()


@pytest.fixture
def production_qmatic_contract() -> Generator[ProjectContract, None, None]:
    yield QMatic.deploy(False, {"from": accounts[DEPLOYER_ACCOUNT_INDEX]})
    chain.reset()


@pytest.fixture
def minted_qmatic_contract(qmatic_contract: ProjectContract) -> ProjectContract:
    mint(
        qmatic_contract=qmatic_contract,
        to=accounts[DEPLOYER_ACCOUNT_INDEX].address,
        amount=DEFAULT_MINT_AMOUNT,
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    return qmatic_contract


@pytest.fixture
def locking_mechanism_first_round_qmatic_contract(
    minted_qmatic_contract: ProjectContract,
) -> ProjectContract:
    initializing_active_balance_locking_mechanism(
        qmatic_contract=minted_qmatic_contract,
        entries=GeneralActiveBalanceLockingMechanismStructure(
            cliff_duration_in_days=3 * MONTH_IN_DAYS,
            linear_release_period_in_days=1 * MONTH_IN_DAYS,
            linear_release_dividend=1,
            linear_release_divisor=10,
            releasing_tge_dividend_on_100=15,
        ),
        caller=accounts[DEPLOYER_ACCOUNT_INDEX],
    )
    return minted_qmatic_contract
