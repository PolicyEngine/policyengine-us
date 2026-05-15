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
        "https://www.alacourt.gov/docs/ALDayCareRates.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.rates
        provider_type = person("al_ccsp_provider_type", period)
        region = person.household("al_ccsp_region", period.this_year)
        age_category = person("al_ccsp_age_category", period)
        quality_tier = person("al_ccsp_quality_tier", period)

        # Look up the full-time rate across the four-dimension matrix.
        # INFORMAL providers are handled separately by a flat weekly cap
        # rather than the matrix; the select() default below carries the
        # informal cap through when the provider type does not match.
        rates = p.maximum_weekly_full_time
        center_rate = rates.CENTER[region][age_category][quality_tier]
        gfdc_rate = rates.GFDC[region][age_category][quality_tier]
        fdc_rate = rates.FDC[region][age_category][quality_tier]

        matrix_rate = select(
            [
                provider_type == ALCCSPProviderType.CENTER,
                provider_type == ALCCSPProviderType.GFDC,
                provider_type == ALCCSPProviderType.FDC,
            ],
            [center_rate, gfdc_rate, fdc_rate],
            default=p.informal_weekly_cap,
        )

        # Part-time (≤25 hours/week) pays half the full-time rate. The
        # informal cap is interpreted as a weekly maximum that applies
        # without halving — providers either bill within the cap or not.
        hours = person("childcare_hours_per_week", period.this_year)
        is_part_time = hours <= p.full_time_hours_threshold
        part_time_rate = matrix_rate * p.part_time_multiplier
        full_time_rate = where(is_part_time, part_time_rate, matrix_rate)

        return where(
            provider_type == ALCCSPProviderType.INFORMAL,
            p.informal_weekly_cap,
            full_time_rate,
        )
