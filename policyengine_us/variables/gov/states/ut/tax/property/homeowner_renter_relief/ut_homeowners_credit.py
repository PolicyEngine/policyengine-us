from policyengine_us.model_api import *


class ut_homeowners_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah homeowner's credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Utah counties apply the homeowner's credit against the claimant's "
        "property taxes accrued, so it lowers the property tax bill instead "
        "of arriving as a payment."
    )
    reference = (
        "https://tax.utah.gov/relief/homeowner-renter-relief/",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=13",
    )
    defined_for = "ut_homeowner_renter_relief_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        income = tax_unit.household(
            "ut_homeowner_renter_relief_household_income", period.last_year
        )
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        return min_(real_estate_taxes, p.maximum.calc(income))
