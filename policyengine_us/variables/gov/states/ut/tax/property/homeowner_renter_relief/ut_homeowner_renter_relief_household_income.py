from policyengine_us.model_api import *


class ut_homeowner_renter_relief_household_income(Variable):
    value_type = float
    entity = Household
    label = "Utah homeowner's/renter's relief household income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.utah.gov/relief/homeowner-renter-relief/",
        "https://files.tax.utah.gov/tax/forms/current/tc-90cb.pdf#page=4",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=1",
    )
    documentation = (
        "Counts adult household members' income: federal adjusted gross income "
        "plus nontaxable income (Utah Code 59-2a-101(15), (17)). A tax unit "
        "dependent's adjusted gross income is on their own return "
        "(dependent_adjusted_gross_income). Members under 18 and members who "
        "are a parent or grandparent of the filer or spouse are left out "
        "(59-2a-101(15)(b))."
    )
    defined_for = StateCode.UT

    def formula(household, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        person = household.members
        person_agi = person("adjusted_gross_income_person", period)
        # Household income counts every member 18 or older (59-2a-101(15)).
        # adjusted_gross_income_person is zero for a tax unit dependent, whose
        # income is on their own return, so a dependent's adjusted gross
        # income comes from that return.
        is_dependent = person("is_tax_unit_dependent", period)
        own_agi = where(
            is_dependent,
            person("dependent_adjusted_gross_income", period),
            person_agi,
        )
        nontaxable_income = person(
            "ut_homeowner_renter_relief_nontaxable_income", period
        )
        is_adult = person("age", period) >= p.adult_age_threshold
        # Income of a member who is a parent or grandparent of the claimant or
        # the claimant's spouse is left out (59-2a-101(15)(b)(ii)).
        parent_or_grandparent = person("is_parent_of_filer_or_spouse", period) | person(
            "is_grandparent_of_filer_or_spouse", period
        )
        counted = is_adult & ~parent_or_grandparent
        tax_unit_person_agi = person.tax_unit.sum(person_agi)
        tax_unit_agi = person.tax_unit("adjusted_gross_income", period)
        tax_unit_has_adult = (
            person.tax_unit("age_head", period) >= p.adult_age_threshold
        ) | (person.tax_unit("age_spouse", period) >= p.adult_age_threshold)
        tax_unit_agi_fallback = (
            (tax_unit_person_agi == 0)
            * person("is_tax_unit_head", period)
            * tax_unit_has_adult
            * tax_unit_agi
        )
        return household.sum(
            (own_agi + nontaxable_income) * counted + tax_unit_agi_fallback
        )
