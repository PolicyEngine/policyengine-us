from policyengine_us.model_api import *


class ca_state_medicaid_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "California state-funded Medicaid enrolled"
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/medi-cal/eligibility/Pages/Medi-Cal-Programs-for-People-with-Medicare.aspx"
    defined_for = "is_ca_state_medicaid_eligible"
    adds = ["takes_up_medicaid_if_eligible"]
