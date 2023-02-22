from typing import TypeAlias, Union

from brownie.exceptions import VirtualMachineError
from brownie.network.account import Account
from brownie.network.contract import ProjectContract

from QMatic.schemas import (
    AttachedLockingMechanismReleasingPeriodStructure,
    Events,
    GeneralActiveBalanceLockingMechanismStructure,
    LinearReleaseShareStructure,
    RevertedMessage,
    WalletBalanceLockingMechanism,
)


def name(qmatic_contract: ProjectContract, caller: Account) -> str:
    return qmatic_contract.name({"from": caller})


def balance_of(
    qmatic_contract: ProjectContract, account_address: str, caller: Account
) -> int:
    return qmatic_contract.balanceOf(account_address, {"from": caller})


def development_status(qmatic_contract: ProjectContract, caller: Account) -> bool:
    return qmatic_contract.IS_DEVELOPMENT({"from": caller})


def max_supply(qmatic_contract: ProjectContract, caller: Account) -> int:
    return qmatic_contract.MAX_SUPPLY({"from": caller})


def mechanism_status(qmatic_contract: ProjectContract, caller: Account) -> bool:
    return qmatic_contract.isMechanismActivated({"from": caller})


def wallet_affected_by_locking_mechanism_state(
    qmatic_contract: ProjectContract, account_address: str, caller: Account
) -> WalletBalanceLockingMechanism:
    data = qmatic_contract.walletsAffectedByLockingMechanism(
        account_address, {"from": caller}
    )
    return WalletBalanceLockingMechanism(
        started_date=data[0],
        total_affected_tokens=data[1],
        linear_release_tokens_per_period=data[2],
        mechanism=GeneralActiveBalanceLockingMechanismStructure(
            cliff_duration_in_days=data[3][0],
            linear_release_period_in_days=data[3][1],
            linear_release_dividend=data[3][2],
            linear_release_divisor=data[3][3],
            releasing_tge_dividend_on_100=data[3][4],
        ),
    )


def last_mechanism_id(qmatic_contract: ProjectContract, caller: Account) -> int:
    return qmatic_contract.lastMechanismId({"from": caller})


def shifted_days(qmatic_contract: ProjectContract, caller: Account) -> int:
    return qmatic_contract.CONTRACT_SHIFT_DAYS({"from": caller})


def active_balance_locking_mechanism(
    qmatic_contract: ProjectContract,
    caller: Account,
) -> GeneralActiveBalanceLockingMechanismStructure:
    data = qmatic_contract.activeBalanceLockingMechanism({"from": caller})
    return GeneralActiveBalanceLockingMechanismStructure(
        cliff_duration_in_days=data[0],
        linear_release_period_in_days=data[1],
        linear_release_dividend=data[2],
        linear_release_divisor=data[3],
        releasing_tge_dividend_on_100=data[4],
    )


def linear_release_dividend_and_divisor_of_address(
    qmatic_contract: ProjectContract, target_address: str, caller: Account
) -> LinearReleaseShareStructure:
    response = qmatic_contract.getLinearReleaseDividendAndDivisorOf(
        target_address, {"from": caller}
    )
    return LinearReleaseShareStructure(dividend=response[0], divisor=response[1])


def linear_release_period_and_amount_of_address(
    qmatic_contract: ProjectContract, target_address: str, caller: Account
) -> AttachedLockingMechanismReleasingPeriodStructure:
    response = qmatic_contract.getLinearReleasePeriodAndAmountOf(
        target_address, {"from": caller}
    )
    return AttachedLockingMechanismReleasingPeriodStructure(
        period_in_days=response[0], release_amount_per_period=response[1]
    )


def remaining_seconds_to_finishing_the_cliff_of_address(
    qmatic_contract: ProjectContract, target_address: str, caller: Account
) -> int:
    return qmatic_contract.getRemainingSecondsToFinishingTheCliffOf(
        target_address, {"from": caller}
    )



def remaining_blocked_tokens_at_now_of_address(
    qmatic_contract: ProjectContract, target_address: str, caller: Account
) -> int:
    return qmatic_contract.getRemainingBlockedTokensAtNowOf(
        target_address, {"from": caller}
    )


def initializing_active_balance_locking_mechanism(
    qmatic_contract: ProjectContract,
    entries: GeneralActiveBalanceLockingMechanismStructure,
    caller: Account,
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:
    try:
        tx = qmatic_contract.initActiveBalanceLockingMechanism(
            entries.cliff_duration_in_days,
            entries.linear_release_period_in_days,
            entries.linear_release_dividend,
            entries.linear_release_divisor,
            entries.releasing_tge_dividend_on_100,
            {"from": caller},
        )
        return Events.from_tx(tx.events), None

    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )


def deactivate_balance_locking_mechanism(
    qmatic_contract: ProjectContract, caller: Account
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:
    try:
        tx = qmatic_contract.deactivateBalanceLockingMechanism(
            {"from": caller},
        )
        return Events.from_tx(tx.events), None
    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )


def contract_locking_for_upgrade(
    qmatic_contract: ProjectContract,
    new_qmatic_address: str,
    report_url: str,
    caller: Account,
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:
    try:
        tx = qmatic_contract.contractLockingForUpgrade(
            new_qmatic_address,
            report_url,
            {"from": caller},
        )
        return Events.from_tx(tx.events), None
    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )


def mint(
    qmatic_contract: ProjectContract,
    to: str,
    amount: int,
    caller: Account,
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:
    try:
        tx = qmatic_contract.mint(
            to,
            amount,
            {"from": caller},
        )
        return Events.from_tx(tx.events), None
    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )


def development_push_date_of_contract(
    qmatic_contract: ProjectContract, days: int, caller: Account
) -> Union[RevertedMessage, None]:
    try:
        tx = qmatic_contract.changeDateOfContract(days, {"from": caller})
        return None
    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return RevertedMessage(msg=error.revert_msg)


def turn_development_mode_off(
    qmatic_contract: ProjectContract, caller: Account
) -> Union[RevertedMessage, None]:
    try:
        qmatic_contract.turnDevelopmentModeOff({"from": caller})
        return None
    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return RevertedMessage(msg=error.revert_msg)


def transfer_with_locking(
    qmatic_contract: ProjectContract, to: str, amount: int, caller: Account
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:
    try:
        tx = qmatic_contract.transferWithLocking(
            to,
            amount,
            {"from": caller},
        )
        return Events.from_tx(tx.events), None

    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )


def transfer_from_user_by_approved_agent(
    qmatic_contract: ProjectContract,
    from_address: str,
    to_address: str,
    amount: int,
    caller: Account,
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:
    try:
        tx = qmatic_contract.transferFrom(
            from_address,
            to_address,
            amount,
            {"from": caller},
        )
        return Events.from_tx(tx.events), None

    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )


def approve_to_spend_tokens_by_agent(
    qmatic_contract: ProjectContract,
    spender_address: str,
    amount_spend: int,
    caller: Account,
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:
    try:
        tx = qmatic_contract.approve(
            spender_address,
            amount_spend,
            {"from": caller},
        )
        return Events.from_tx(tx.events), None
    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )


def normal_transfer(
    qmatic_contract: ProjectContract, to: str, amount: int, caller: Account
) -> tuple[Union[Events, None], Union[RevertedMessage, None]]:

    try:
        tx = qmatic_contract.transfer(
            to,
            amount,
            {"from": caller},
        )
        return Events.from_tx(tx.events), None
    except VirtualMachineError as error:
        if error.revert_type != "revert":
            raise
        return (
            None,
            RevertedMessage(msg=error.revert_msg),
        )
