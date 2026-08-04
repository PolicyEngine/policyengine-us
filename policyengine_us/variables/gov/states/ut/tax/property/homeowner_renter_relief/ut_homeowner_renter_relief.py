from policyengine_us.model_api import *


class ut_homeowner_renter_relief(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Homeowner's/Renter's Relief"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.utah.gov/relief/homeowner-renter-relief/",
        "https://files.tax.utah.gov/tax/forms/current/tc-90cb.pdf#page=4",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=11",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=14",
    )
    defined_for = "ut_homeowner_renter_relief_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        renter_income = tax_unit.household(
            "ut_homeowner_renter_relief_household_income", period
        )
        homeowner_income = tax_unit.household(
            "ut_homeowner_renter_relief_household_income", period.last_year
        )
        renter_maximum = p.maximum.calc(renter_income)
        homeowner_maximum = p.maximum.calc(homeowner_income)
        rent = add(tax_unit, period, ["rent"])
        renter_credit = min_(rent * p.renter.rate.calc(renter_income), renter_maximum)
        homeowner_credit = min_(
            add(tax_unit, period, ["real_estate_taxes"]), homeowner_maximum
        )
        return renter_credit + homeowner_credit
