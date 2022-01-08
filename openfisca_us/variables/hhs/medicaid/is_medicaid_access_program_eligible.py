from openfisca_us.model_api import *

# class medicaid_access_program_eligible(Variable):
#     value_type = bool
#     entity = Person
#     definition_period = YEAR
#     label = "Eligible for MCAP"
#     documentation = (
#         "Whether the person is Medicaid Access Program Eligible"
#     )
#     def formula(person, period, parameters):
#         income = person.spm_unit("medicaid_gross_income", period)
#         fpg = person.spm_unit("spm_unit_fpg", period)
#         fpg_income_threshold = person("medicaid_income_threshold", period)
#         pregnant = person("is_pregnant", period)
#         income_share_of_fpg = income / fpg
#         return ( ((income_share_of_fpg <= 3.22) & (income_share_of_fpg > 2.13) & pregnant)
#         )
