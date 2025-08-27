from policyengine_us.model_api import *


class id_liheap_seasonal_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP seasonal heating assistance benefit"
    definition_period = MONTH
    defined_for = StateCode.ID
    unit = USD
    documentation = "Seasonal heating assistance benefit amount for Idaho LIHEAP (October-March)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.83",
    ]

    def formula(spm_unit, period, parameters):
        # Seasonal heating assistance is available October 1 - March 31
        month = period.start.month
        heating_season = parameters(
            period
        ).gov.states.id.idhw.liheap.heating_season
        is_heating_season = (month >= heating_season.start_month) | (
            month <= heating_season.end_month
        )

        # Must be eligible for LIHEAP
        eligible = spm_unit("id_liheap_eligible", period)

        # Get benefit parameters
        p = parameters(period).gov.states.id.idhw.liheap.seasonal_benefit
        minimum_benefit = p.minimum
        maximum_benefit = p.maximum

        # Idaho determines benefits based on income, household size, geographic location,
        # and energy burden. For now, we'll use a simplified calculation
        # that provides the minimum benefit to eligible households during heating season

        # In practice, benefit amount varies based on:
        # - Household income relative to poverty guidelines
        # - Household composition
        # - Service costs
        # - Energy burden relative to income and household size

        # For this implementation, provide minimum benefit during heating season
        benefit_amount = where(
            eligible & is_heating_season, minimum_benefit, 0
        )

        return benefit_amount
