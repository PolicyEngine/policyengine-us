from policyengine_us.model_api import *


class ut_homeowner_renter_relief_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Utah Homeowner's/Renter's Relief"
    definition_period = YEAR
    reference = (
        "https://tax.utah.gov/relief/homeowner-renter-relief/",
        "https://tax.utah.gov/relief/renter-refund/",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=1",
    )
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        age_eligible = (age_head >= p.age_threshold) | (age_spouse >= p.age_threshold)
        surviving_spouse = filing_status == statuses.SURVIVING_SPOUSE
        income = tax_unit("adjusted_gross_income", period)
        paid_rent_or_property_tax = (
            add(tax_unit, period, ["rent", "real_estate_taxes"]) > 0
        )
        return (
            (age_eligible | surviving_spouse)
            & (income <= p.income_limit)
            & paid_rent_or_property_tax
        )
