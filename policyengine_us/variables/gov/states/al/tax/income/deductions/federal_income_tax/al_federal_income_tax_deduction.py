from policyengine_us.model_api import *


class al_federal_income_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama federal income tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf#page=20"
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.federal_tax
        income_sources = add(tax_unit, period, p.countable_sources)
        federal_credits = add(tax_unit, period, p.credits)
        return max_(income_sources - federal_credits, 0)
