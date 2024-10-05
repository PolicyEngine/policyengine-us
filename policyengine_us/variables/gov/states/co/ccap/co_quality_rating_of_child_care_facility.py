from policyengine_us.model_api import *


class co_quality_rating_of_child_care_facility(Variable):
    value_type = int
    entity = Person
    label = "Quality rating of child care facility for Colorado Child Care Assistance Program"
    definition_period = YEAR
    # defined_for = StateCode.CO
