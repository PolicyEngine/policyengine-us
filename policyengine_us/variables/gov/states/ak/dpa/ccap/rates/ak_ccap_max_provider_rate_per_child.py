from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ak.dpa.ccap.rates.ak_ccap_provider_type import (
    AKCCAPProviderType,
)
from policyengine_us.variables.gov.states.ak.dpa.ccap.rates.ak_ccap_care_schedule import (
    AKCCAPCareSchedule,
)


class ak_ccap_max_provider_rate_per_child(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP maximum provider reimbursement rate per child"
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.rates
        provider_type = person("ak_ccap_provider_type", period)
        care_schedule = person("ak_ccap_care_schedule", period)
        age_group = person("ak_ccap_age_group", period)
        region = person.spm_unit("ak_ccap_rate_region", period)
        attending_days = person("childcare_attending_days_per_month", period.this_year)

        is_part_day = (care_schedule == AKCCAPCareSchedule.PT_MONTH) | (
            care_schedule == AKCCAPCareSchedule.PT_DAY
        )
        day_schedule = where(
            is_part_day, AKCCAPCareSchedule.PT_DAY, AKCCAPCareSchedule.FT_DAY
        )
        month_schedule = where(
            is_part_day, AKCCAPCareSchedule.PT_MONTH, AKCCAPCareSchedule.FT_MONTH
        )

        provider_conditions = [
            provider_type == AKCCAPProviderType.LICENSED_CENTER,
            provider_type == AKCCAPProviderType.LICENSED_GROUP_HOME,
            provider_type == AKCCAPProviderType.LICENSED_HOME,
            provider_type == AKCCAPProviderType.APPROVED_RELATIVE_IN_HOME,
        ]
        day_rate = select(
            provider_conditions,
            [
                p.licensed_center[day_schedule][region][age_group],
                p.licensed_group_home[day_schedule][region][age_group],
                p.licensed_home[day_schedule][region][age_group],
                p.approved_relative_in_home[day_schedule][region][age_group],
            ],
        )
        month_rate = select(
            provider_conditions,
            [
                p.licensed_center[month_schedule][region][age_group],
                p.licensed_group_home[month_schedule][region][age_group],
                p.licensed_home[month_schedule][region][age_group],
                p.approved_relative_in_home[month_schedule][region][age_group],
            ],
        )

        return where(attending_days > 0, day_rate * attending_days, month_rate)
