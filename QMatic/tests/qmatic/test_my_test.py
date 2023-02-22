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
