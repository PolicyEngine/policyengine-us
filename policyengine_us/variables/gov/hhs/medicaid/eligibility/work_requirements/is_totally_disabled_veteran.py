from policyengine_us.model_api import *


class is_totally_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Medicaid CE exemption for disabled veterans"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters):
        vet_disability_minimum: int = parameters(period).gov.hhs.medicaid.eligibility.work_requirements.total_veteran_disability_minimum

        is_veteran = person("is_veteran", period)
        veteran_disability_rating = person(
            "veteran_disability_rating", period
        )
        
        return is_veteran and veteran_disability_rating >= vet_disability_minimum
    
