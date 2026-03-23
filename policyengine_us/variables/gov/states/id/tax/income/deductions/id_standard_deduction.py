from policyengine_us.model_api import *


class id_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_09-29-2025.pdf#page=9",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_10-23-2024.pdf#page=8",
    )

    def formula(tax_unit, period, parameters):
        # Idaho matched the federal standard deduction through 2024. In 2025,
        # Form 40 moved to state-specific base amounts while keeping the same
        # aged/blind worksheet structure.
        if period.start.year < 2025:
            return tax_unit("standard_deduction", period)

        p = parameters(period).gov.states.id.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        separate_filer_itemizes = tax_unit("separate_filer_itemizes", period)
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period) | tax_unit(
            "spouse_is_dependent_elsewhere", period
        )

        base_amount = p.base_amount[filing_status]
        dependent_amount = min_(
            base_amount,
            max_(tax_unit("tax_unit_earned_income", period) + 450, 1_350),
        )
        core_deduction = select(
            [separate_filer_itemizes, dependent_elsewhere],
            [0, dependent_amount],
            default=base_amount,
        )
        additional_amount = p.additional_amount[filing_status]
        return core_deduction + additional_amount * tax_unit("aged_blind_count", period)
