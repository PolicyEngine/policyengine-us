from policyengine_us.model_api import *


class nj_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey total income"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        nj_additions = tax_unit("nj_agi_additions", period)
        nj_subtractions = tax_unit("nj_agi_subtractions", period)
        return max_(0, agi + nj_additions - nj_subtractions)
