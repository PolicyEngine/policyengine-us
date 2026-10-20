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
        "https://www.law.cornell.edu/uscode/text/8/1622#b",
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
        spouse = nh_ssp_spouse(person, period)
        size = person("nh_ssp_assistance_group_size", period)
        # A group larger than the person and any spouse includes an essential person.
        essential = size > 1 + (spouse >= 0)
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
        # before August 22, 1996. AAM 305.11 exempts the listed statuses, as
        # 8 USC 1622(b)(1) requires.
        # NOTE: AAM 305.13 keeps "lawfully admitted permanent residents
        # regardless of work history" out for the 5 years. 8 USC
        # 1622(b)(2) instead makes a permanent resident credited with 40
        # qualifying quarters (8 USC 1645) "eligible for any State public
        # benefits", and He-W 616.02 does not address it. The model follows
        # 8 USC 1622(b)(2). AAM 305.13 may instead rest on 8 USC 1624, which
        # lets a State restrict aliens' eligibility for "programs of general
        # cash public assistance" if no more restrictive than comparable
        # Federal programs; SSI bars these residents for the 5 years (8 USC
        # 1613(a)). Whether the adult categories are general cash public
        # assistance is unsettled. The quarters come from
        # snap_alien_qualifying_quarters, the same legal count, which defaults
        # to 0, so the exception applies only when quarters are supplied.
        immigration = person("immigration_status", period.this_year)
        statuses = immigration.possible_values
        citizen = immigration == statuses.CITIZEN
        exempt = np.isin(immigration.decode_to_str(), p.immigration.exempt_statuses)
        quarters = person("snap_alien_qualifying_quarters", period.this_year)
        credited_permanent_resident = (
            immigration == statuses.LEGAL_PERMANENT_RESIDENT
        ) & (quarters >= p.immigration.permanent_resident_qualifying_quarters)
        waited = (
            person("years_since_us_entry", period.this_year)
            >= p.immigration.waiting_period
        )
        immigration_eligible = person(
            "is_citizen_or_legal_immigrant", period.this_year
        ) & (citizen | exempt | credited_permanent_resident | waited)
        return (
            (aged | blind | disabled)
            & (resources <= p.resource_limit)
            & immigration_eligible
            & (arrangement != la.NONE)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
        )
