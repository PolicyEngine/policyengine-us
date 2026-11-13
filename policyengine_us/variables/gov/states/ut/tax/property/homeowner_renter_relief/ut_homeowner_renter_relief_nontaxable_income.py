from policyengine_us.model_api import *


class ut_homeowner_renter_relief_nontaxable_income(Variable):
    value_type = float
    entity = Person
    label = "Utah homeowner's/renter's relief nontaxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=5"
    )
    defined_for = StateCode.UT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        listed_sources = add(person, period, p.nontaxable_income.sources)
        social_security = person("social_security", period)
        ssdi = person("social_security_disability", period)
        # A tax unit dependent's taxable Social Security is on their own return
        # (dependent_adjusted_gross_income); taxable_social_security holds only
        # the head's and spouse's.
        is_dependent = person("is_tax_unit_dependent", period)
        taxable_social_security = where(
            is_dependent,
            person("dependent_taxable_social_security", period),
            person("taxable_social_security", period),
        )
        nontaxable_social_security = max_(
            0, social_security - ssdi - taxable_social_security
        )
        total_unemployment_compensation = person(
            "total_unemployment_compensation", period
        )
        taxable_unemployment_compensation = person(
            "taxable_unemployment_compensation", period
        )
        # A dependent's adjusted gross income already counts all of their
        # unemployment compensation, so none of it is added here.
        nontaxable_unemployment_compensation = ~is_dependent * max_(
            0,
            total_unemployment_compensation - taxable_unemployment_compensation,
        )
        return (
            listed_sources
            + nontaxable_social_security
            + nontaxable_unemployment_compensation
        )
