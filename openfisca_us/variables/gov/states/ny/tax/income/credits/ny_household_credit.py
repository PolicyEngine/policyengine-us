from openfisca_us.model_api import *
import numpy as np


class ny_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY household credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (b)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        in_ny = tax_unit.household("state_code_str", period) == "NY"
        p = parameters(
            period
        ).gov.states.ny.tax.income.credits.household_credit
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        # Include spouse's AGI if filing separately.
        agi = add(
            tax_unit,
            period,
            ["adjusted_gross_income", "spouse_separate_adjusted_gross_income"],
        )
        # Single filers: based only on AGI.
        single = filing_status == filing_statuses.SINGLE
        # Use `right=True` to reflect "over...but not over".
        amount_if_single = p.single.calc(agi, right=True)
        single_amount = single * amount_if_single
        # All others are based on AGI & size.
        # In the case of married filing separate, based on the combined AGI and size.
        size = add(
            tax_unit,
            period,
            ["tax_unit_size", "spouse_separate_tax_unit_size"],
        )
        separate = filing_status == filing_statuses.SEPARATE
        non_single_base = p.non_single.base.calc(agi, right=True)
        non_single_additional = p.non_single.additional.calc(agi, right=True)
        total_amount_if_not_single = (
            non_single_base + non_single_additional * (size - 1)
        )
        amount_if_not_single = np.ceil(
            total_amount_if_not_single / where(separate, 2, 1)
        )
        non_single_amount = amount_if_not_single * ~single
        return in_ny * (single_amount + non_single_amount)
