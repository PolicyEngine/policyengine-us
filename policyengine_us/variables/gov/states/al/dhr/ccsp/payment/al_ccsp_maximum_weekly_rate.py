from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.al.dhr.ccsp.al_ccsp_provider_type import (
    ALCCSPProviderType,
)


class al_ccsp_maximum_weekly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alabama CCSP maximum weekly reimbursement rate per child"
    definition_period = MONTH
    defined_for = "al_ccsp_eligible_child"
    reference = (
        "Alabama DHR Provider Rate Chart",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/Provider-Rates-with-QRIS-Tiers-April-1-2022-b.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.rates
        provider_type = person("al_ccsp_provider_type", period)
        region = person.household("al_ccsp_region", period.this_year)
        age_category = person("al_ccsp_age_category", period)
        quality_tier = person("al_ccsp_quality_tier", period)

        rates = p.maximum_weekly_full_time
        center_rate = rates.CENTER[region][age_category][quality_tier]
        gfdc_rate = rates.GFDC[region][age_category][quality_tier]
        fdc_rate = rates.FDC[region][age_category][quality_tier]

        # INFORMAL providers use the flat informal_weekly_cap as their
        # full-time rate; the matrix is not consulted for them.
        full_time_rate = select(
            [
                provider_type == ALCCSPProviderType.CENTER,
                provider_type == ALCCSPProviderType.GFDC,
                provider_type == ALCCSPProviderType.FDC,
            ],
            [center_rate, gfdc_rate, fdc_rate],
            default=p.informal_weekly_cap,
        )

        # Part-time (≤25 hours/week) pays half the applicable full-time
        # rate, including for INFORMAL providers (so the part-time cap is
        # half of informal_weekly_cap).
        hours = person("childcare_hours_per_week", period.this_year)
        is_part_time = hours <= p.full_time_hours_threshold
        return where(
            is_part_time,
            full_time_rate * p.part_time_multiplier,
            full_time_rate,
        )
