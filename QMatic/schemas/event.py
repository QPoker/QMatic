from typing import Union

from brownie import ZERO_ADDRESS
from pydantic import BaseModel, Field

from QMatic.tests.constants import BOOL_DEFAULT_VALUE, INT_DEFAULT_VALUE, STRING_DEFAULT


class BalanceLockingMechanismUpdateLog(BaseModel):
    mechanism_id: int = Field(INT_DEFAULT_VALUE, alias="mechanismId")
    cliff_duration_in_days: int = Field(INT_DEFAULT_VALUE, alias="cliffDurationInDays")
    linear_release_period_in_days: int = Field(
        INT_DEFAULT_VALUE, alias="linearReleasePeriodInDays"
    )
    linear_release_dividend: int = Field(
        INT_DEFAULT_VALUE, alias="linearReleaseDividend"
    )
    linear_release_divisor: int = Field(INT_DEFAULT_VALUE, alias="linearReleaseDivisor")
    releasing_tge__dividend_on_100: int = Field(
        INT_DEFAULT_VALUE, alias="releasingTGEDividendOn100"
    )
    is_active: bool = Field(BOOL_DEFAULT_VALUE, alias="isActive")


class UpgradingQMatic(BaseModel):
    new_token_contract_address: str = Field(ZERO_ADDRESS, alias="newQMaticAddress")
    upgrade_date: int = Field(INT_DEFAULT_VALUE, alias="upgradeDate")
    event_report_url: str = Field(STRING_DEFAULT, alias="eventReportUrl")


class InvestmentWithLockingMechanismScenario(BaseModel):
    mechanism_id: int = Field(INT_DEFAULT_VALUE, alias="mechanismId")
    account_address: str = Field(ZERO_ADDRESS, alias="account")
    started_date: int = Field(INT_DEFAULT_VALUE, alias="startedDate")
    linear_release_tokens_per_period: int = Field(
        INT_DEFAULT_VALUE, alias="linearReleaseTokensPerPeriod"
    )
    amount_of_invest_in_qmatic: int = Field(
        INT_DEFAULT_VALUE, alias="amountOfInvestInQMatic"
    )
    total_affected_tokens: int = Field(INT_DEFAULT_VALUE, alias="totalAffectedTokens")


class Transfer(BaseModel):
    from_address: str = Field(ZERO_ADDRESS, alias="from")
    to_address: str = Field(ZERO_ADDRESS, alias="to")
    value: int = Field(INT_DEFAULT_VALUE, alias="value")


class Approval(BaseModel):
    owner: str = Field(ZERO_ADDRESS, alias="owner")
    spender: str = Field(ZERO_ADDRESS, alias="spender")
    value: int = Field(INT_DEFAULT_VALUE, alias="value")


class Events(BaseModel):
    transfer: Union[list[Transfer], None] = Field(None, alias="Transfer")
    investment_with_locking_mechanism_scenario: Union[
        list[InvestmentWithLockingMechanismScenario],
        None,
    ] = Field(None, alias="InvestmentWithLockingMechanismScenario")
    balance_locking_mechanism_update_log: Union[
        list[BalanceLockingMechanismUpdateLog], None
    ] = Field(None, alias="BalanceLockingMechanismUpdateLog")
    contract_upgrade: Union[list[UpgradingQMatic], None] = Field(
        None, alias="UpgradingQMatic"
    )
    approval: Union[list[Approval], None] = Field(None, alias="Approval")

    @classmethod
    def from_tx(cls, obj_in: dict) -> "Events":
        return cls(
            **{  # type: ignore
                event_name: [events] if isinstance(events, dict) else list(events)
                for event_name, events in obj_in.items()
            }
        )
