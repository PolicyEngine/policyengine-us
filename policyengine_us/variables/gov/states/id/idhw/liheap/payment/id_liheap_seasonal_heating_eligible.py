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
        in_heating_season = (month >= 10) | (month <= 3)

        # Must be LIHEAP eligible and in heating season
        eligible = spm_unit("id_liheap_eligible", period)

        return eligible & in_heating_season
