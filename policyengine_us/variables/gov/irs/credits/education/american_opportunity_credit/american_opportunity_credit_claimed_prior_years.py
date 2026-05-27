from policyengine_us.model_api import *


class american_opportunity_credit_claimed_prior_years(Variable):
    value_type = int
    entity = Person
    label = "Prior years claiming the American Opportunity or Hope Credit"
    documentation = "Number of prior tax years for which the American Opportunity Credit or former Hope Credit was claimed for the student."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
