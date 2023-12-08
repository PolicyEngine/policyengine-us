from policyengine_us.model_api import *


class la_general_relief_housing_subsidy_program_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Los Angeles County General Relief Housing Subsidy based on the program eligibility"
    definition_period = YEAR
    # Person has to be a resident of LA County
    defined_for = "la_general_relief_eligible"
    reference = "https://dpss.lacounty.gov/en/cash/gr/housing.html"
