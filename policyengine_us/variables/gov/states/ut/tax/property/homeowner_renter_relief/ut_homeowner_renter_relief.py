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
    adds = ["ut_renters_credit", "ut_homeowners_credit"]
