from policyengine_us.model_api import *


class ri_liheap_priority_household(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Rhode Island LIHEAP priority household"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.priority
        person = spm_unit.members
        age = person("age", period)

        has_elderly = spm_unit.any(age >= p.elderly_age)
        has_disabled = spm_unit.any(person("is_disabled", period))
        has_young_child = spm_unit.any(age < p.young_child_age)

        return has_elderly | has_disabled | has_young_child
