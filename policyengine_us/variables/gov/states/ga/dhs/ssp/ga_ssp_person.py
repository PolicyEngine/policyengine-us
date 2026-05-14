from policyengine_us.model_api import *


class ga_ssp_person(Variable):
    value_type = float
    entity = Person
    label = "Georgia State Supplementary Payment per person"
    unit = USD
    definition_period = MONTH
    defined_for = "ga_ssp_eligible_person"
    reference = "https://pamms.dhs.ga.gov/dfcs/medicaid/2578/"
    adds = ["gov.states.ga.dhs.ssp.amount"]
