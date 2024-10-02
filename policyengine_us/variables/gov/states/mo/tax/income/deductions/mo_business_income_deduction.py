from policyengine_us.model_api import *


class mo_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri business income deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2023.pdf#page=16",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.022",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mo.tax.income.deductions.business_income
        qualified_business_income = add(
            tax_unit, period, ["qualified_business_income"]
        )
        total_qualified_business_income = tax_unit.sum(
            qualified_business_income
        )
        return p.rate * qualified_business_income
