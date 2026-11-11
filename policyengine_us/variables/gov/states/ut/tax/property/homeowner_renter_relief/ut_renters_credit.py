from policyengine_us.model_api import *


class ut_renters_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah renter's credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The Utah State Tax Commission pays the renter's credit from the "
        "General Fund on the claimant's own application, outside the income "
        "tax return."
    )
    reference = (
        "https://tax.utah.gov/relief/renter-refund/",
        "https://files.tax.utah.gov/tax/forms/current/tc-90cb.pdf#page=4",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=11",
    )
    defined_for = "ut_homeowner_renter_relief_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        income = tax_unit.household(
            "ut_homeowner_renter_relief_household_income", period
        )
        rent = add(tax_unit, period, ["rent"])
        return min_(rent * p.renter.rate.calc(income), p.maximum.calc(income))
