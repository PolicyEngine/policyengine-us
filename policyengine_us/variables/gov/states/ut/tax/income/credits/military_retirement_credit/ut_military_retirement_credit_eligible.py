from policyengine_us.model_api import *


class ut_military_retirement_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Utah military retirement credit"
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1043.html"
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        # Has military retirement pay
        military_retirement_pay = add(
            tax_unit, period, ["military_retirement_pay"]
        )
        has_military_retirement_pay = military_retirement_pay > 0
        # Cannot claim if claiming the retirement credit (code 18)
        claims_retirement_credit = tax_unit(
            "ut_claims_retirement_credit", period
        )
        return has_military_retirement_pay & ~claims_retirement_credit
