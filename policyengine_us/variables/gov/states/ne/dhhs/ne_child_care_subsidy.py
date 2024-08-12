from policyengine_us.model_api import *


class ne_child_care_subsidy(Variable):
    value_type = float
    entity = Person
    label = "Amount of Nebraska Child Care Subsidy program benefit"
    definition_period = YEAR
    defined_for = "ne_child_care_subsidy_eligible"
