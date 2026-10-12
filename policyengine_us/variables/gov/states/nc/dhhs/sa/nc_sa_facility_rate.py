from policyengine_us.model_api import *


class nc_sa_facility_rate(Variable):
    value_type = float
    entity = Person
    label = "North Carolina SA contracted monthly care rate"
    definition_period = MONTH
    unit = USD
    documentation = "Defaults to the published rate. Supply the actual rate if a facility contracts for less. In-home payments use the published basic or enhanced rate."
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf",
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.dhhs.sa
        setting = person("nc_sa_care_setting", period)
        settings = setting.possible_values
        enhanced = (setting == settings.SPECIAL_CARE_UNIT) | (
            setting == settings.IN_HOME_ENHANCED
        )
        return where(enhanced, p.rate.enhanced, p.rate.basic)
