from policyengine_us.model_api import *


class meets_snap_work_requirements_person(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = "https://www.fns.usda.gov/snap/work-requirements"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.usda.snap.work_requirements.abawd
        
        # Check if person meets general work requirements
        meets_general = person("meets_snap_general_work_requirements", period)
        
        # Determine if person is an ABAWD (no dependent children in household)
        age = person("monthly_age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < p.age_threshold.dependent
        has_dependent_child = person.spm_unit.sum(is_dependent & is_child) > 0
        
        # Check if person is in ABAWD age range (not exempt by age)
        # Person is exempt if under 18 or 55+ (will be 65+ in 2027)
        age_exempt = p.age_threshold.exempted.calc(age)
        is_abawd_age = ~age_exempt
        
        # Person is an ABAWD if they're in the age range and have no dependent children
        is_abawd = is_abawd_age & ~has_dependent_child
        
        # If person is an ABAWD, they must meet both general AND ABAWD requirements
        # Otherwise, they only need to meet general requirements
        meets_abawd = person("meets_snap_work_requirements", period)
        
        return where(
            is_abawd,
            meets_general & meets_abawd,
            meets_general
        )
