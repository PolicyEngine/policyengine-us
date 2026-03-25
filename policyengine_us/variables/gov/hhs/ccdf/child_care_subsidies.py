from policyengine_us.model_api import *


class child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Child care subsidies"
    unit = USD

    adds = "gov.hhs.ccdf.child_care_subsidy_programs"
