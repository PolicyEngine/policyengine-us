from policyengine_us.model_api import *


class KYCCAPDayLength(Enum):
    FULL_DAY = "Full day (5 or more hours)"
    PART_DAY = "Part day (under 5 hours)"


class ky_ccap_day_length(Variable):
    value_type = Enum
    entity = Person
    possible_values = KYCCAPDayLength
    default_value = KYCCAPDayLength.FULL_DAY
    definition_period = MONTH
    label = "Kentucky CCAP day length"
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=2"

    def formula(person, period, parameters):
        # 922 KAR 2:160 Section 1(13) defines a full day as 5 or more hours and
        # Section 1(21) defines a part day as under 5 hours.
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        p = parameters(period).gov.states.ky.dcbs.ccap.rates
        is_full_day = hours_per_day >= p.full_day_min_hours
        return where(
            is_full_day,
            KYCCAPDayLength.FULL_DAY,
            KYCCAPDayLength.PART_DAY,
        )
