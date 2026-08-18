from policyengine_us.model_api import *


class ut_ui_quarters_with_wages(Variable):
    value_type = int
    entity = Person
    label = "Utah UI base-period quarters with wages"
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R994-401-201"
    )
    # Number of base-period calendar quarters (0-4) in which the claimant
    # earned wages. Utah Admin Code R994-401-201 requires wages in at least
    # two base-period quarters.
    # Defaults to 0, so in microsimulation (where this input is not populated)
    # claimants are treated as having wages in no base-period quarters.
