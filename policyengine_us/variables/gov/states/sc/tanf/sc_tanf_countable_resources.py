from policyengine_us.model_api import *


class sc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF countable resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    adds = "gov.states.sc.tanf.resources.list"
