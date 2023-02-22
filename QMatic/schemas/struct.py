from typing import Union

from brownie import ZERO_ADDRESS
from pydantic import BaseModel, Field

from QMatic.tests.constants import BOOL_DEFAULT_VALUE, INT_DEFAULT_VALUE, STRING_DEFAULT


class GeneralActiveBalanceLockingMechanismStructure(BaseModel):
    cliff_duration_in_days: int = INT_DEFAULT_VALUE
    linear_release_period_in_days: int = INT_DEFAULT_VALUE
    linear_release_dividend: int = INT_DEFAULT_VALUE
    linear_release_divisor: int = INT_DEFAULT_VALUE
    releasing_tge_dividend_on_100: int = INT_DEFAULT_VALUE


class WalletBalanceLockingMechanism(BaseModel):
    started_date: int = INT_DEFAULT_VALUE
    total_affected_tokens: int = INT_DEFAULT_VALUE
    linear_release_tokens_per_period: int = INT_DEFAULT_VALUE
    mechanism: Union[GeneralActiveBalanceLockingMechanismStructure, None] = None


class LinearReleaseShareStructure(BaseModel):
    divisor: int = INT_DEFAULT_VALUE
    dividend: int = INT_DEFAULT_VALUE


class AttachedLockingMechanismReleasingPeriodStructure(BaseModel):
    period_in_days: int = INT_DEFAULT_VALUE
    release_amount_per_period: int = INT_DEFAULT_VALUE
