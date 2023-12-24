from policyengine_us.model_api import *


class ut_ss_benefits_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Social Security Benefits Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        claims_retirement_credit = tax_unit(
            "ut_claims_retirement_credit", period
        )
        max_credit = tax_unit("ut_ss_benefits_credit_max", period)
        return ~claims_retirement_credit * max_credit
