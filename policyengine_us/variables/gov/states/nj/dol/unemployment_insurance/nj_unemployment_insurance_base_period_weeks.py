from policyengine_us.model_api import *


class nj_unemployment_insurance_base_period_weeks(Variable):
    value_type = int
    entity = Person
    label = "New Jersey unemployment insurance base period weeks worked"
    unit = "week"
    documentation = "Number of weeks worked during the base period for New Jersey unemployment insurance eligibility. A base week is any week in which the claimant earned at least the minimum base week earnings threshold."
    definition_period = YEAR
    defined_for = StateCode.NJ
