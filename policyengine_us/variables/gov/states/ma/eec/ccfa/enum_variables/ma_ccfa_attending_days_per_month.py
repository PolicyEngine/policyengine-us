from policyengine_us.model_api import *


class ma_ccfa_attending_days_per_month(Variable):
    value_type = int
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) attending days per month"
    definition_period = MONTH
    defined_for = StateCode.MA
