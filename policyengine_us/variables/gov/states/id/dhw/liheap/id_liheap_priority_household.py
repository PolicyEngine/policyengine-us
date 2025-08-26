from policyengine_us.model_api import *


class id_liheap_priority_household(Variable):
    value_type = bool
    entity = Person
    label = "Idaho LIHEAP priority household member"
    definition_period = YEAR
    reference = "https://healthandwelfare.idaho.gov/services-programs/financial-assistance/home-heating-and-utility-assistance/"
    documentation = "Priority households include those with children under 6, elderly (65+), or disabled members"

    def formula(person, period, parameters):
        # Get parameters
        p = parameters(period).gov.states.id.dhw.liheap.priority_groups
        
        # Check each priority condition
        age = person("age", period)
        is_disabled = person("is_disabled", period)
        
        # Check if household has young children
        spm_unit = person.spm_unit
        ages_in_unit = spm_unit.members("age", period)
        has_young_child = spm_unit.any(ages_in_unit < p.child_age_threshold)
        
        # Check if household has elderly members
        has_elderly = spm_unit.any(ages_in_unit >= p.elderly_age_threshold)
        
        # Check if household has disabled members
        disabilities_in_unit = spm_unit.members("is_disabled", period)
        has_disabled = spm_unit.any(disabilities_in_unit)
        
        # Household is priority if any condition is met
        return has_young_child | has_elderly | has_disabled