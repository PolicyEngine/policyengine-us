from policyengine_us.model_api import *


class id_liheap_priority_group(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP priority group"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household qualifies as priority group for Idaho LIHEAP (children under 6, elderly, or disabled members)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.82(a)(2)",
    ]

    def formula(spm_unit, period, parameters):
        # Get age thresholds from parameters
        p = parameters(period).gov.states.id.idhw.liheap.priority_age_threshold
        child_age_threshold = p.child
        elderly_age_threshold = p.elderly

        # Check for children under 6
        # Age is defined per year, so use the year containing this month
        year_str = str(period.start.year)
        person_ages = spm_unit.members("age", year_str)
        has_young_child = (person_ages < child_age_threshold).any()

        # Check for elderly members (60+ or 65+)
        has_elderly = (person_ages >= elderly_age_threshold).any()

        # Check for disabled members
        has_disabled = spm_unit.members("is_disabled", period).any()

        return has_young_child | has_elderly | has_disabled
