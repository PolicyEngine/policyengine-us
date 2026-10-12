from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.il.dhs.ccap.rates.il_ccap_base_day_type import (
    ILCCAPBaseDayType,
)
from policyengine_us.variables.gov.states.il.dhs.ccap.rates.il_ccap_provider_type import (
    ILCCAPProviderType,
)


class il_ccap_max_daily_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Illinois CCAP maximum daily base provider rate"
    defined_for = "il_ccap_eligible_child"
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=173323",
        # Center rates are on page 1; home rates continue on page 2.
        "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/pages/ccap-for-providers/IL444-4343%20-%20Child%20Care%20Payment%20Rates%20for%20Child%20Care%20Providers%207.1.26.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap
        provider_type = person("il_ccap_provider_type", period)
        county_group = person.household("il_ccap_county_group", period)
        age_group = person("il_ccap_child_age_group", period)

        full_day = ILCCAPBaseDayType.FULL_DAY
        part_day = ILCCAPBaseDayType.PART_DAY
        licensed_center_full = p.rates.licensed_center[county_group][age_group][
            full_day.name
        ]
        licensed_center_part = p.rates.licensed_center[county_group][age_group][
            part_day.name
        ]
        exempt_center_full = p.rates.license_exempt_center[county_group][age_group][
            full_day.name
        ]
        exempt_center_part = p.rates.license_exempt_center[county_group][age_group][
            part_day.name
        ]
        licensed_home_full = p.rates.licensed_home[county_group][age_group][
            full_day.name
        ]
        licensed_home_part = p.rates.licensed_home[county_group][age_group][
            part_day.name
        ]
        exempt_home_full = p.rates.license_exempt_home[full_day.name]
        exempt_home_part = p.rates.license_exempt_home[part_day.name]

        full_day_rate = select(
            [
                provider_type == ILCCAPProviderType.LICENSED_CENTER,
                provider_type == ILCCAPProviderType.LICENSE_EXEMPT_CENTER,
                provider_type == ILCCAPProviderType.LICENSED_HOME,
                provider_type == ILCCAPProviderType.LICENSE_EXEMPT_HOME,
            ],
            [
                licensed_center_full,
                exempt_center_full,
                licensed_home_full,
                exempt_home_full,
            ],
            default=0,
        )
        part_day_rate = select(
            [
                provider_type == ILCCAPProviderType.LICENSED_CENTER,
                provider_type == ILCCAPProviderType.LICENSE_EXEMPT_CENTER,
                provider_type == ILCCAPProviderType.LICENSED_HOME,
                provider_type == ILCCAPProviderType.LICENSE_EXEMPT_HOME,
            ],
            [
                licensed_center_part,
                exempt_center_part,
                licensed_home_part,
                exempt_home_part,
            ],
            default=0,
        )
        duration = person("il_ccap_care_duration", period)
        full_day_units = p.rates.duration.full_day_units[duration]
        part_day_units = p.rates.duration.part_day_units[duration]
        maximum_rate = full_day_rate * full_day_units + part_day_rate * part_day_units
        return where(p.in_effect, maximum_rate, 0)
