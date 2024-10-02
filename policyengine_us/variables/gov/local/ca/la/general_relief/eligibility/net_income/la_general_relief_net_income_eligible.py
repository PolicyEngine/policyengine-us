from policyengine_us.model_api import *


class la_general_relief_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Los Angeles County General Relief based on the net income requirements"
    definition_period = MONTH
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        net_income = add(spm_unit, period, ["la_general_relief_net_income"])
        limit = spm_unit("la_general_relief_net_income_limit", period)
        return net_income < limit
