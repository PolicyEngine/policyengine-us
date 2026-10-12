from policyengine_us.model_api import *


class is_enrolled_at_least_half_time_for_american_opportunity_credit(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled at least half-time for the American Opportunity Credit"
    documentation = "Whether the student is enrolled at least half-time for at least one academic period beginning in the tax year for American Opportunity Credit purposes."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
