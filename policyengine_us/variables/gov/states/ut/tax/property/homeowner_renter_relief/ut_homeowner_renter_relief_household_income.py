from policyengine_us.model_api import *


class ut_homeowner_renter_relief_household_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah homeowner's/renter's relief household income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.utah.gov/relief/homeowner-renter-relief/",
        "https://files.tax.utah.gov/tax/forms/current/tc-90cb.pdf#page=4",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=1",
    )
    documentation = (
        "Counts adult household members' adjusted gross income. Parent and "
        "grandparent exclusions are not modeled because household relationship "
        "data do not identify those relatives."
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        person = spm_unit.members
        person_agi = person("adjusted_gross_income_person", period)
        is_adult = person("age", period) >= p.adult_age_threshold
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
        return spm_unit.sum(person_agi * is_adult + tax_unit_agi_fallback)
