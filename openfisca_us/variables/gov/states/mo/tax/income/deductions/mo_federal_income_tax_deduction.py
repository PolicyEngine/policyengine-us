from openfisca_us.model_api import *


class mo_federal_income_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO Federal income tax deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=8",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.171&bid=49937&hl=federal+income+tax+deduction%u2044",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        federal_tax = tax_unit("income_tax", period)
        # Subtract CARES act credits, only affects year 2020.
        # https://revisor.mo.gov/main/OneSection.aspx?section=143.171&bid=48731
        cares_rebate = tax_unit("rrc_cares", period)
        # Law is vague, but for now, limit to nonnegative income tax.
        federal_tax_less_cares = max_(federal_tax - cares_rebate, 0)
        # Apply rate based on AGI.
        rate = parameters(
            period
        ).gov.states.mo.tax.income.deductions.federal_income_tax.rate.calc(
            tax_unit("mo_adjusted_gross_income", period)
        )
        uncapped = federal_tax_less_cares * rate
        # Apply cap based on filing status.
        cap = parameters(
            period
        ).gov.states.mo.tax.income.deductions.federal_income_tax.cap[
            tax_unit("filing_status", period)
        ]
        return min_(uncapped, cap)
