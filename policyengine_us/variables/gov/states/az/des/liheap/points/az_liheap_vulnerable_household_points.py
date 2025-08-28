from policyengine_us.model_api import *


class az_liheap_vulnerable_household_points(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP vulnerable household points"
    definition_period = YEAR
    defined_for = "az_liheap_eligible"
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap
        points = p.points.vulnerable_household

        # Check for elderly members (60+)
        person = spm_unit.members
        age = person("age", period)
        has_elderly = spm_unit.any(age >= p.minimum_age_elderly)

        # Check for disabled members
        has_disabled = spm_unit.any(person("is_disabled", period))

        # Check for children under 6
        has_young_child = spm_unit.any(age < p.maximum_child_age)

        # Calculate points - cumulative for each category
        elderly_points = where(has_elderly, points.elderly, 0)
        disabled_points = where(has_disabled, points.disabled, 0)
        child_points = where(has_young_child, points.child_under_6, 0)

        # Return cumulative points from all vulnerability categories
        return elderly_points + disabled_points + child_points
