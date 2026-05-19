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
        pre_eligible = tax_unit(
            "ut_homeowner_renter_relief_pre_one_claimant_eligible", period
        )
        selected_claimant = tax_unit(
            "ut_homeowner_renter_relief_selected_claimant", period
        )
        return pre_eligible & selected_claimant
