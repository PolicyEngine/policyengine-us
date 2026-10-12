from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.sd.dss.cca.rates.sd_cca_provider_type import (
    SDCCAProviderType,
)


class sd_cca_weekly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "South Dakota CCA weekly maximum reimbursement rate per child"
    definition_period = MONTH
    defined_for = "sd_cca_eligible_child"
    reference = "https://dss.sd.gov/docs/childcare/assistance/CCA_Weekly_Reimbursement_Rates.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.rates
        region = person.household("sd_cca_region", period)
        age_group = person("sd_cca_age_group", period)
        time_category = person("sd_cca_time_category", period)
        provider_type = person("sd_cca_provider_type", period)
        family_day_care_rate = p.weekly.family_day_care[region][age_group][
            time_category
        ]
        licensed_center_rate = p.weekly.licensed_center[region][age_group][
            time_category
        ]
        # Informal, in-home, and relative rates are flat statewide (no region or
        # age variation), so they are keyed only by level of service.
        informal_rate = p.weekly.informal[time_category]
        base_rate = select(
            [
                provider_type == SDCCAProviderType.FAMILY_DAY_CARE,
                provider_type == SDCCAProviderType.LICENSED_CENTER,
                provider_type == SDCCAProviderType.INFORMAL,
            ],
            [family_day_care_rate, licensed_center_rate, informal_rate],
            default=licensed_center_rate,
        )
        # A provider caring for a child with special needs may receive the base
        # rate plus an additional 75% of that rate. is_disabled proxies the
        # special-needs determination. The multiplier raises the rate ceiling,
        # so it folds inside the expense cap applied in sd_cca.
        is_disabled = person("is_disabled", period.this_year)
        special_needs_multiplier = where(is_disabled, p.special_needs_multiplier, 1)
        return base_rate * special_needs_multiplier
