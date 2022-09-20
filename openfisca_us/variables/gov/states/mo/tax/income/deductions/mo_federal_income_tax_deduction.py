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
        mo_adjusted_gross_income = tax_unit("mo_adjusted_gross_income", period)
        federal_tax = tax_unit("income_tax", period)

        # subtract CARES act credits, only affects year 2020, source: https://revisor.mo.gov/main/OneSection.aspx?section=143.171&bid=48731
        cares_rebate = tax_unit("rrc_cares", period)
        federal_tax_less_cares = federal_tax - cares_rebate

        filing_status = tax_unit("filing_status", period)

        federal_income_tax_deduction_rates = parameters(
            period
        ).gov.states.mo.tax.income.deductions.federal_income_tax_deduction_rates
        rate = federal_income_tax_deduction_rates.calc(
            mo_adjusted_gross_income
        )
        federal_income_tax_deduction_amount = federal_tax_less_cares * rate

        federal_income_tax_deduction_cap = parameters(
            period
        ).gov.states.mo.tax.income.deductions.federal_income_tax_deduction_caps[
            filing_status
        ]

        return min_(
            federal_income_tax_deduction_amount,
            federal_income_tax_deduction_cap,
        )
