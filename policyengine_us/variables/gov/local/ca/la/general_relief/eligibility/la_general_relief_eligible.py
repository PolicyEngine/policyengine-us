from policyengine_us.model_api import *


class la_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Los Angeles County General Relief"
    definition_period = MONTH
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        age_eligible = spm_unit("la_general_relief_age_eligible", period)
        cash_eligible = spm_unit(
            "la_general_relief_cash_asset_eligible", period
        )
        home_value_eligible = spm_unit(
            "la_general_relief_home_value_eligible", period
        )
        motor_vehicle_value_eligible = spm_unit(
            "la_general_relief_motor_vehicle_value_eligible", period
        )
        net_income_eligible = spm_unit(
            "la_general_relief_net_income_eligible", period
        )
        personal_property_eligible = spm_unit(
            "la_general_relief_personal_property_eligible", period
        )
        disability_eligible = spm_unit(
            "la_general_relief_disability_eligible", period
        )
        immigration_status_eligible = spm_unit(
            "la_general_relief_immigration_status_eligible", period
        )
        return (
            age_eligible
            & cash_eligible
            & home_value_eligible
            & motor_vehicle_value_eligible
            & net_income_eligible
            & personal_property_eligible
            & immigration_status_eligible
        )
