# =============================================================================
# nm_deductions.py
#
# This replaces the old "nm_deductions" logic.
#   - Includes SALT add-back (line 10)
#   - Uses the appropriate federal deduction (line 12)
#   - Adds other NM-specific deductions
# =============================================================================

import numpy as np

from policyengine_us.model_api import (
    Variable,
    TaxUnit,
    YEAR,
    StateCode,
    add,
    min_,
    max_,
    select,
    where,
)


class nm_salt_addback(Variable):
    """
    New Mexico SALT add-back (PIT-1 line 10).

    If the taxpayer itemizes on their federal return, they must add back
    some/all state & local taxes deducted on federal Schedule A.
    Matches the 10-step worksheet in NM PIT-1 instructions.
    """

    value_type = float
    entity = TaxUnit
    label = "New Mexico SALT add-back (PIT-1 line 10)"
    unit = "USD"
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)

        # (1) SALT income portion (federal Sch A, line 5a)
        fed_salt_income = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )

        # (2) total SALT = SALT income + real_estate_taxes (and possibly personal property if separate)
        fed_real_estate = tax_unit("real_estate_taxes", period)
        fed_salt_total = fed_salt_income + fed_real_estate

        # (3) ratio = (line 1) / (line 2)
        ratio = np.zeros_like(fed_salt_total)
        mask = fed_salt_total != 0
        ratio[mask] = fed_salt_income[mask] / fed_salt_total[mask]

        # (4) SALT actually claimed on fed Sch A (line 5e), limited by SALT cap
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions
        salt_cap = p.itemized.salt_and_real_estate.cap[filing_status]
        fed_salt_claimed = min_(salt_cap, fed_salt_total)

        # (5) line 4 * line 3
        salted_income_part = fed_salt_claimed * ratio

        # (6) min(line 4, line 5)
        line6 = min_(fed_salt_claimed, salted_income_part)

        # (7) Federal standard deduction
        fed_standard = tax_unit("standard_deduction", period)

        # (8) total federal itemized from Form 1040 line 12
        fed_itemized_total = tax_unit("federal_itemized_deduction", period)

        # (9) difference between itemized total and standard deduction
        diff_itemized_std = max_(fed_itemized_total - fed_standard, 0)

        # (10) SALT add-back = lesser of line6 and diff_itemized_std
        salt_addback = min_(line6, diff_itemized_std)

        # If not itemizing on federal return, no SALT add-back
        return where(itemizes, salt_addback, 0)


class nm_federal_deduction_for_nm(Variable):
    """
    New Mexico PIT-1 line 12:
      - If fed standard was used, line 12 is that standard deduction.
      - If itemized, line 12 = total federal itemized.
    """

    value_type = float
    entity = TaxUnit
    label = "Federal deduction carried over to NM (PIT-1 line 12)"
    unit = "USD"
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        fed_standard = tax_unit("standard_deduction", period)
        fed_itemized_total = tax_unit("federal_itemized_deduction", period)

        return where(itemizes, fed_itemized_total, fed_standard)


class nm_deductions(Variable):
    """
    Final New Mexico deductions = (federal deduction for NM, line 12)
                                - (SALT add-back, line 10)
                                + (other NM-specific deductions).
    """

    value_type = float
    entity = TaxUnit
    label = "New Mexico income deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        fed_ded_for_nm = tax_unit("nm_federal_deduction_for_nm", period)
        salt_addback = tax_unit("nm_salt_addback", period)

        # Add all other NM-specific deductions
        OTHER_DEDUCTIONS = [
            "nm_medical_care_expense_deduction",
            "nm_deduction_for_certain_dependents",
            "nm_net_capital_gains_deduction",
        ]
        other_nmdeds = add(tax_unit, period, OTHER_DEDUCTIONS)

        # Net NM Deductions
        return fed_ded_for_nm - salt_addback + other_nmdeds
