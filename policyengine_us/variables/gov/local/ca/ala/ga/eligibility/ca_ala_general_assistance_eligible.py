from policyengine_us.model_api import *


class ca_ala_general_assistance_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alameda County General Assistance"
    definition_period = MONTH
    # Person has to be a resident of Alameda County
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    def formula(spm_unit, period, parameters):
        age_eligible = spm_unit("ca_ala_general_assistance_age_eligible", period)
        asset_eligible = spm_unit("ca_ala_general_assistance_asset_eligible", period)
        immigration_status_eligible = spm_unit(
            "ca_ala_general_assistance_immigration_status_eligible", period
        )
        net_income_eligible = spm_unit(
            "ca_ala_general_assistance_income_eligible", period
        )
        # Check if person has dependent children (ineligible if they do)
        has_dependent_children = spm_unit("spm_unit_children", period) > 0
        
        return (
            age_eligible
            & asset_eligible
            & immigration_status_eligible
            & net_income_eligible
            & ~has_dependent_children
        )
