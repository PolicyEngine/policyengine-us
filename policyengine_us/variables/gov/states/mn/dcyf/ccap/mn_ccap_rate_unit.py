from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mn.dcyf.ccap.mn_ccap_provider_type import (
    MNCCAPProviderType,
)


class MNCCAPRateUnit(Enum):
    WEEKLY = "Weekly"
    FULL_DAY = "Full day"
    HOURLY = "Hourly"
    LNL_HOURLY = "Legal non-licensed hourly"


class mn_ccap_rate_unit(Variable):
    value_type = Enum
    entity = Person
    possible_values = MNCCAPRateUnit
    default_value = MNCCAPRateUnit.HOURLY
    definition_period = MONTH
    label = "Minnesota CCAP rate unit"
    defined_for = StateCode.MN
    reference = (
        # Minnesota CCAP Policy Manual section 9.9; Minn. Stat. 142E.17 subd. 1(f).
        "https://www.revisor.mn.gov/statutes/cite/142E.17",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.ccap.rate_unit
        hours_per_week = person("childcare_hours_per_week", period.this_year)
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        provider_type = person("mn_ccap_provider_type", period)
        # Section 9.9: weekly rate when authorized care exceeds 35 hours per
        # week; full-day rate when 35 or fewer hours per week but more than 5
        # hours per day; hourly otherwise.
        weekly = hours_per_week > p.weekly_hours_threshold
        full_day = hours_per_day > p.daily_hours_threshold
        # Legal non-licensed providers are paid only on an hourly basis.
        is_lnl = provider_type == MNCCAPProviderType.LEGAL_NON_LICENSED
        return select(
            [
                is_lnl,
                weekly,
                full_day,
            ],
            [
                MNCCAPRateUnit.LNL_HOURLY,
                MNCCAPRateUnit.WEEKLY,
                MNCCAPRateUnit.FULL_DAY,
            ],
            default=MNCCAPRateUnit.HOURLY,
        )
