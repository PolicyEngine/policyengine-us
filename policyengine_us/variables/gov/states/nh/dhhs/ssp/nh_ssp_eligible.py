from policyengine_us.model_api import *


class nh_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "New Hampshire adult cash assistance non-income eligibility"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = (
        "https://gc.nh.gov/rsa/html/XII/167/167-6.htm",
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ssp
        age = person("age", period.this_year)
        aged = age >= parameters(period).gov.ssa.ssi.eligibility.aged_threshold
        blind = person("is_blind", period.this_year)
        disabled = (age >= p.disabled_minimum_age) & person(
            "nh_ssp_disability_eligible", period.this_year
        )
        arrangement = person("nh_ssp_living_arrangement", period)
        la = arrangement.possible_values
        independent = arrangement == la.INDEPENDENT
        couple = independent & (person.marital_unit.sum(independent) == 2)
        essential = independent & person.marital_unit.any(
            person("nh_ssp_has_essential_person", period)
        )
        resources = person("ssi_countable_resources", period.this_year)
        resources = where(couple, person.marital_unit.sum(resources), resources)
        resources = resources + person("nh_ssp_resources_deemed_from_parents", period)
        resources = resources + essential * person.marital_unit.max(
            max_(person("nh_ssp_essential_person_resources", period), 0)
        )
        immigration = person("immigration_status", period.this_year)
        citizen = immigration == immigration.possible_values.CITIZEN
        immigrant = person("is_ssi_qualified_noncitizen", period.this_year)
        return (
            (aged | blind | disabled)
            & (resources <= p.resource_limit)
            & (citizen | immigrant)
            & (arrangement != la.NONE)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
        )
