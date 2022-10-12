from policyengine_us.model_api import *


class is_eligible_for_american_opportunity_credit(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for American Opportunity Credit"
    documentation = "Whether the person is eligible for the AOC in respect of qualified tuition expenses for this tax year. The expenses must be for one of the first four years of post-secondary education, and the person must not have claimed the AOC for any four previous tax years."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#b_2"
