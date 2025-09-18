from policyengine_us.model_api import *


class ca_state_medicaid(Variable):
    value_type = float
    entity = Person
    label = "California state-funded Medicaid"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/medi-cal/eligibility/Pages/Medi-Cal-Programs-for-People-with-Medicare.aspx"
    adds = ["ca_state_medicaid_cost_if_enrolled"]
