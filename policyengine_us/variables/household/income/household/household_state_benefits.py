from policyengine_us.model_api import *


class household_state_benefits(Variable):
    value_type = float
    entity = Household
    label = "household State benefits"
    unit = USD
    documentation = "Benefits paid by State agencies."
    definition_period = YEAR
    adds = [
        "state_supplement",
        "co_state_supplement",
        # State child care subsidies.
        "ca_child_care_subsidies",
        "co_child_care_subsidies",
        "ca_cvrp",  # California Clean Vehicle Rebate Project.
        "ca_care",
        "ca_fera",
        "ca_la_ez_save",
        "co_oap",
    ]
    exhaustive_parameter_dependencies = "gov.states"
