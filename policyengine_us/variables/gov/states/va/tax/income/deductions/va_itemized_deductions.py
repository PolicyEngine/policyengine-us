from policyengine_us.model_api import *


class va_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2021/schedule-2021.pdf"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p_va = parameters(period).gov.states.va.tax.income.deductions.itemized

        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        uncapped_state_and_local_tax = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        va_itm_deds = (
            itm_deds_less_salt
            + uncapped_property_taxes
            + uncapped_state_and_local_tax
        )

        federal_agi = tax_unit("adjusted_gross_income", period)

        filing_status = tax_unit("filing_status", period)
        applicable_amount = p_va.applicable_amount[filing_status]

        # Output if deductions are not limited
        itemized_ded_reduced_by_uncapped_state_and_local = max_(
            va_itm_deds - uncapped_state_and_local_tax, 0
        )
        # Output if deductions are limited
        selected_ded_reduced_by_reduced_state_and_local = tax_unit(
            "va_reduced_itemized_deductions", period
        )
        return where(
            federal_agi > applicable_amount,
            selected_ded_reduced_by_reduced_state_and_local,
            itemized_ded_reduced_by_uncapped_state_and_local,
        )
