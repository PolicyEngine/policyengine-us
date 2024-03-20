from policyengine_us.model_api import *


class sc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "SC TANF countable resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    adds = "gov.states.sc.tanf.eligibility.resource_list"
