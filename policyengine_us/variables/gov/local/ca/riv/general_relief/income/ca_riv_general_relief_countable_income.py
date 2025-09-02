from policyengine_us.model_api import *


class ca_riv_general_relief_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County General Relief countable income"
    definition_period = MONTH
    defined_for = "in_riv"

    # This value cannot be negative because the exclusion is calculated
    # as a fraction of the excluded person's income, determined by
    # household size and the number of applicants.
    adds = ["ca_riv_general_relief_countable_income_person"]
    subtracts = ["ca_riv_general_relief_excluded_income"]
