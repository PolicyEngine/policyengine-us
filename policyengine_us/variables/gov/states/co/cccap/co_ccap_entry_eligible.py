from policyengine_us.model_api import *


# class co_ccap_entry_eligible(Variable):
#     # value_type = str
#     entity = TaxUnit
#     label = "Colorado"
#     unit = USD
#     definition_period = YEAR
#     defined_for = StateCode.CO

#     def formula(tax_unit, period, parameters):
#         p = parameters(period).gov.states.co.cccap
        
#         # agi = tax_unit("adjusted_gross_income", period)
#         # county = tax_unit.household("county_str", period)
#         # print(county)
#         # return county
#         # county = tax_unit.household("county_str", period)
#         return p.entry_threshold.ADAMS_COUNTY_CO


class co_ccap_entry_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        income = tax_unit("co_taxable_income", period)
        rate = parameters(period).gov.states.co.tax.income.rate
        return income * rate
