from policyengine_us.model_api import *


class id_liheap_seasonal_heating_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP seasonal heating assistance eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household is eligible for seasonal heating assistance (October-March)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
    ]

    def formula(spm_unit, period, parameters):
        # Seasonal heating is only available October through March
        month = period.start.month
        heating_season = parameters(
            period
        ).gov.states.id.idhw.liheap.heating_season
        in_heating_season = (month >= heating_season.start_month) | (
            month <= heating_season.end_month
        )

        # Must be LIHEAP eligible and in heating season
        eligible = spm_unit("id_liheap_eligible", period)

        return eligible & in_heating_season
