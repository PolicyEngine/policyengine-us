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
        taxable_social_security = person("taxable_social_security", period)
        nontaxable_social_security = max_(
            0, social_security - ssdi - taxable_social_security
        )
        unemployment_compensation = person("unemployment_compensation", period)
        taxable_unemployment_compensation = person(
            "taxable_unemployment_compensation", period
        )
        nontaxable_unemployment_compensation = max_(
            0,
            unemployment_compensation - taxable_unemployment_compensation,
        )
        return (
            listed_sources
            + nontaxable_social_security
            + nontaxable_unemployment_compensation
        )
