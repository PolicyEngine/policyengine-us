from policyengine_us.model_api import *


class nj_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        total_income = tax_unit("nj_total_income", period)
        p = parameters(period).gov.states.nj.tax.income
        exclusions = add(tax_unit, period, p.all_exclusions)
        return max_(0, total_income - exclusions)
