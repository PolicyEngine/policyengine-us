from policyengine_us.model_api import *


class is_medically_frail(Variable):
    value_type = bool
    entity = Person
    label = "The community engagement rules for Medicaid CE define a few different conditions for medical frailty or special needs"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters) -> bool:
        is_blind: bool = person("is_blind", period)
        is_ssi_disabled: bool = person("is_ssi_disabled", period)
        has_substance_use_disorder: bool = person("has_substance_use_disorder", period)
        has_disabling_mental_disorder: bool = person("has_disabling_mental_disorder", period)
        has_adl_impairment: bool = person("has_adl_impairment", period)
        has_serious_or_complex_medical_condition: bool = person("has_serious_or_complex_medical_condition", period)
        
        
        return (
            is_blind or
            is_ssi_disabled or
            has_substance_use_disorder or
            has_disabling_mental_disorder or
            has_adl_impairment or
            has_serious_or_complex_medical_condition
        )
