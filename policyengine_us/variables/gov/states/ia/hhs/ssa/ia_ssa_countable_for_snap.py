from policyengine_us.model_api import *


class ia_ssa_countable_for_snap(Variable):
    value_type = float
    entity = Person
    label = "Iowa State Supplementary Assistance countable for SNAP"
    definition_period = MONTH
    unit = USD
    reference = "https://hhs.iowa.gov/media/3997#page=34"

    def formula(person, period, parameters):
        category = person("ia_ssa_category", period)
        home_care = category == category.possible_values.IN_HOME_CARE
        # The blind supplement remains ordinary cash assistance when paid
        # alongside the excluded reimbursement for in-home health care.
        return where(
            home_care, person("ia_ssa_federal", period), person("ia_ssa", period)
        )
