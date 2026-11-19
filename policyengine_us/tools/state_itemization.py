from itertools import product

import numpy as np

from policyengine_us.tools.period_branch import get_override_branch, has_input
from policyengine_us.variables.gov.states.tax.income.state_deduction_method import (
    StateDeductionMethod,
)

STANDARD = StateDeductionMethod.STANDARD.index
ITEMIZED = StateDeductionMethod.ITEMIZED.index
AUTOMATIC = StateDeductionMethod.AUTOMATIC.index
STATE_METHOD_COUNT = len(StateDeductionMethod)
JOINT_METHOD_COUNT = 2 * STATE_METHOD_COUNT
JOINT_FILING_CHOICE_COUNT = 2 * JOINT_METHOD_COUNT
CENT = 0.01
SALT_ELECTION_WHEN_STATE_ITEMIZED = ("MD", "MO")
SALT_ELECTION_STATES = (*SALT_ELECTION_WHEN_STATE_ITEMIZED, "NE", "VA")
NATIVE_STATE_ELECTION_INPUTS = {
    "AR": "ar_tax_unit_itemizes",
    "CA": "ca_itemizes",
    "DE": "de_tax_unit_itemizes",
    "HI": "hi_itemizes",
    "ID": "id_itemizes",
    "KY": "ky_tax_unit_itemizes",
    "MN": "mn_itemizing",
    "MS": "ms_tax_unit_itemizes",
    "NY": "ny_itemizes",
}


def joint_itemization_is_enabled(period, parameters):
    """The resident election rules have been verified for tax year 2025."""
    return (
        period.start.year == 2025
        and parameters(period).gov.simulation.joint_federal_state_itemization
    )


def joint_federal_itemizes(choices):
    return choices % JOINT_METHOD_COUNT >= STATE_METHOD_COUNT


def joint_uses_alternative(choices):
    return choices % JOINT_FILING_CHOICE_COUNT >= JOINT_METHOD_COUNT


def state_itemization_uses_itemized(method, automatic):
    """Resolve a state method with the jurisdiction's usual calculation."""
    return np.where(
        method == StateDeductionMethod.AUTOMATIC,
        automatic,
        method == StateDeductionMethod.ITEMIZED,
    )


def choose_joint_itemization(costs, federal_methods, prefer_federal_itemized):
    """Choose within a cent of the global minimum, then prefer the federal tie rule."""
    minimum = np.min(costs, axis=0)
    if not np.isfinite(minimum).all():
        raise ValueError("Every tax unit needs a legal finite deduction election.")
    within_cent = costs - minimum <= CENT
    same_as_preferred = np.asarray(federal_methods)[:, None] == np.asarray(
        prefer_federal_itemized
    )
    preferred = within_cent & same_as_preferred
    return np.where(preferred.any(axis=0), preferred, within_cent).argmax(axis=0)


def joint_itemization(tax_unit, period, parameters):
    """Evaluate 2025 full-year resident deduction elections on isolated branches."""
    if not tax_unit.count:
        return np.empty(0, dtype=np.int32)
    sim = tax_unit.simulation
    state = tax_unit.household("state_code_str", period)
    p = parameters(period).gov.simulation.resident_itemization
    independent = np.isin(state, p.independent_states)
    federal_itemizers_only = np.isin(state, p.federal_itemizers_only)
    follows_federal = np.isin(state, p.follows_federal)
    elected_state = independent | federal_itemizers_only
    status = tax_unit("filing_status", period)
    requires_federal_itemizing = (status == status.possible_values.SEPARATE) & tax_unit(
        "separate_filer_itemizes", period
    )
    forced_federal = (
        tax_unit("tax_unit_itemizes", period)
        if has_input(sim, "tax_unit_itemizes", period)
        else None
    )
    state_supplied = has_input(sim, "state_deduction_method", period)
    forced_state = (
        np.asarray(tax_unit("state_deduction_method", period))
        if state_supplied
        else np.full(tax_unit.count, AUTOMATIC)
    )
    keep_automatic = state_supplied & (forced_state == AUTOMATIC)
    native_supplied = np.full(tax_unit.count, AUTOMATIC)
    for jurisdiction, variable in NATIVE_STATE_ELECTION_INPUTS.items():
        residents = state == jurisdiction
        if residents.any() and has_input(sim, variable, period):
            declared = np.where(tax_unit(variable, period), ITEMIZED, STANDARD)
            native_supplied = np.where(residents, declared, native_supplied)
    fixed_tuition = has_input(sim, "ny_elects_tuition_credit_when_itemizing", period)
    fixed_salt = has_input(sim, "state_and_local_sales_tax_elected", period)
    known_salt_components = not has_input(
        sim, "state_and_local_sales_or_income_tax", period
    )
    any_claim_of_right = tax_unit("claim_of_right_section_1341_eligible", period).any()
    choices = []
    federal_methods = []
    costs = []
    prefer_federal_itemized = None
    for federal_itemizes, trial in product(
        (False, True), ("standard", "itemized", "alternative")
    ):
        allowable = federal_itemizes | ~requires_federal_itemizing
        if forced_federal is not None:
            allowable &= forced_federal == federal_itemizes
        linked_method = ITEMIZED if federal_itemizes else STANDARD
        linked = np.where(follows_federal, linked_method, AUTOMATIC)
        if trial == "standard":
            methods = np.where(elected_state, STANDARD, linked)
            allowable &= ~(
                np.isin(state, ("ID", "MO", "NC"))
                & requires_federal_itemizing
                & ~keep_automatic
            )
        elif trial == "itemized":
            methods = np.where(elected_state, ITEMIZED, linked)
            allowable &= independent | (federal_itemizes & federal_itemizers_only)
            allowable &= ~keep_automatic
        else:
            # Each resident can use only one of these alternatives.
            ny_tuition = (state == "NY") & (not fixed_tuition)
            salt_sales = (
                np.isin(state, SALT_ELECTION_STATES)
                & federal_itemizes
                & (not fixed_salt)
                & known_salt_components
            )
            methods = np.where(
                (state == "NY") | federal_itemizers_only, ITEMIZED, linked
            )
            allowable &= ny_tuition | salt_sales
        if not allowable.any():
            continue
        methods = np.where(keep_automatic, AUTOMATIC, methods)

        method_code = STATE_METHOD_COUNT * federal_itemizes
        if trial == "alternative":
            method_code += JOINT_METHOD_COUNT
        branch_name = f"resident_itemization_{period.start.year}_{method_code}_{trial}"
        branch = get_override_branch(
            sim,
            branch_name,
            period,
            {
                "tax_unit_itemizes": np.full(tax_unit.count, federal_itemizes),
                "state_deduction_method": methods,
                "tax_unit_joint_itemization": method_code + methods,
            },
            inherit_calculated=False,
        )
        try:
            if (allowable & (state == "HI")).any():
                eligibility = branch.calculate(
                    "hi_itemized_deductions_eligible"
                    if trial == "itemized"
                    else "hi_required_to_itemize",
                    period,
                )
                allowable &= (state != "HI") | (
                    eligibility
                    if trial == "itemized"
                    else (keep_automatic | ~eligibility)
                )
            ny_items = (state == "NY") & (
                (methods == ITEMIZED) | (keep_automatic & (native_supplied == ITEMIZED))
            )
            if (allowable & ny_items).any():
                # N.Y. Tax Law §613 requires the standard deduction when the
                # elected itemized amount is smaller, including the tuition option.
                allowable &= ~ny_items | (
                    branch.calculate("ny_itemized_deductions", period)
                    >= branch.calculate("ny_standard_deduction", period)
                )
            # Local liability differs from the Schedule A measure of taxes paid.
            total = np.asarray(branch.calculate("income_tax", period), dtype=float)
            total = total + branch.calculate("state_income_tax", period)
            total += branch.calculate("local_tax", period)
            claim_of_right_credit = (
                branch.calculate("claim_of_right_credit_applies", period)
                if any_claim_of_right
                else False
            )
            if prefer_federal_itemized is None:
                prefer_federal_itemized = branch.calculate(
                    "itemized_taxable_income_deductions", period
                ) > branch.calculate("standard_deduction", period)
            methods = resolved_state_methods(
                branch, period, state, methods, federal_itemizes
            )
        finally:
            sim.branches.pop(branch_name)
        del branch
        methods = np.where(keep_automatic, AUTOMATIC, methods)
        allowable &= (forced_state == AUTOMATIC) | (forced_state == methods)
        allowable &= (
            keep_automatic
            | (native_supplied == AUTOMATIC)
            | (native_supplied == methods)
        )
        choices.append(
            method_code + methods + JOINT_FILING_CHOICE_COUNT * claim_of_right_credit
        )
        federal_methods.append(federal_itemizes)
        costs.append(np.where(allowable, total, np.inf))

    if not choices:
        raise ValueError("Every tax unit needs a legal deduction election.")
    selected = choose_joint_itemization(
        np.stack(costs), federal_methods, prefer_federal_itemized
    )
    return np.stack(choices)[selected, np.arange(tax_unit.count)]


def resolved_state_methods(branch, period, state, methods, federal_itemizes):
    """Report the actual method where a jurisdiction requires the larger amount."""
    for name in ("OR", "NE"):
        residents = state == name
        if residents.any():
            prefix = name.lower()
            if name == "NE" and not federal_itemizes:
                resolved = STANDARD
            else:
                itemized = branch.calculate(f"{prefix}_itemized_deductions", period)
                standard = branch.calculate(f"{prefix}_standard_deduction", period)
                resolved = np.where(itemized > standard, ITEMIZED, STANDARD)
            methods = np.where(residents, resolved, methods)
    return methods
