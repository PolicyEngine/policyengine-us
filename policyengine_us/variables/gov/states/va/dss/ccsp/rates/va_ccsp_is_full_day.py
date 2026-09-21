from policyengine_us.model_api import *
from policyengine_us.tools.childcare import childcare_hours_for_daily_schedule


class va_ccsp_is_full_day(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    default_value = True
    label = "Virginia CCSP full day care"
    defined_for = StateCode.VA
    reference = "https://www.childcare.virginia.gov/home/showpublisheddocument/66667/638981099706730000#page=203"

    def formula(person, period, parameters):
        hours = childcare_hours_for_daily_schedule(person, period)
        p = parameters(period).gov.states.va.dss.ccsp.maximum_reimbursement_rate
        # Zero also represents unknown hours. Explicit authorizations remain
        # inputs, including full-day authorization for unavailable part-day care.
        return (hours == 0) | (hours >= p.full_day_min_hours)
