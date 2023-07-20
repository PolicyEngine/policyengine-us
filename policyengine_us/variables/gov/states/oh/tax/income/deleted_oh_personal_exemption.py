# from policyengine_us.model_api import *


# class oh_personal_exemption(Variable):
#     value_type = float
#     entity = TaxUnit
#     label = "OH Personal Exemption"
#     defined_for = StateCode.OH
#     unit = USD
#     definition_period = YEAR
#     reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14"

#     def formula(tax_unit, period, parameters):
#         agi = tax_unit("oh_agi", period)
#         num_of_dependents = tax_unit("tax_unit_dependents", period)
#         p = parameters(period).gov.states.oh.tax.income
#         personal_exemption_amount = p.exemption.personal.calc(agi)
#         return (
#             num_of_dependents + eligible_spouse + eligible_head
#         ) * personal_exemption_amount
