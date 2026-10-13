from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nh.dhhs.ssp._nh_ssp_couple import (
    nh_ssp_spouse,
    spouse_value,
)


class nh_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "New Hampshire adult cash assistance non-income eligibility"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = (
        "https://gc.nh.gov/rsa/html/XII/167/167-6.htm",
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
        "https://dhhs.nh.gov/aam_htm/html/305_11_qualified_aliens_eligible_without_restriction_aam.htm",
        "https://dhhs.nh.gov/aam_htm/html/305_13_qualified_aliens_with_restricted_eligibility_based_on_date_of_entry_into_the_us_aam.htm",
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
        spouse = nh_ssp_spouse(person, period)
        has_essential_person = person("nh_ssp_has_essential_person", period)
        essential = independent & (
            has_essential_person | spouse_value(has_essential_person, spouse, False)
        )
        resources = person("ssi_countable_resources", period.this_year)
        resources = resources + spouse_value(resources, spouse)
        resources = resources + person("nh_ssp_resources_deemed_from_parents", period)
        essential_resources = max_(
            person("nh_ssp_essential_person_resources", period), 0
        )
        resources = resources + essential * max_(
            essential_resources, spouse_value(essential_resources, spouse)
        )
        # He-W 616.02(a): qualified aliens under 8 USC 1641(b) are eligible once
        # the waiting period since entry has elapsed, which also covers entry
        # before August 22, 1996. AAM 305.11 exempts the listed statuses; AAM
        # 305.13 applies the wait to permanent residents regardless of work
        # history, so SSI's 40-quarter rule does not apply.
        immigration = person("immigration_status", period.this_year)
        citizen = immigration == immigration.possible_values.CITIZEN
        exempt = np.isin(immigration.decode_to_str(), p.immigration.exempt_statuses)
        waited = (
            person("years_since_us_entry", period.this_year)
            >= p.immigration.waiting_period
        )
        immigration_eligible = person(
            "is_citizen_or_legal_immigrant", period.this_year
        ) & (citizen | exempt | waited)
        return (
            (aged | blind | disabled)
            & (resources <= p.resource_limit)
            & immigration_eligible
            & (arrangement != la.NONE)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
        )
