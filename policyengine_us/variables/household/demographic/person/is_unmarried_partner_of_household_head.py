from policyengine_us.model_api import *


class is_unmarried_partner_of_household_head(Variable):
    value_type = bool
    entity = Person
    label = "is unmarried partner of household head"
    definition_period = YEAR
