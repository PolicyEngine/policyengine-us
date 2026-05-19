from policyengine_us.model_api import *


class fl_tca_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA gross income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-65A-4-220",
        "https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per DCF 2620.0109.01: Gross income test - NO disregards applied
        # "The standard earned income disregard, 200 and 1/2 which includes
        # the standard earned income disregard of $90, is not deducted in this test."
        p = parameters(period).gov.states.fl.dcf.tanf.income.gross_test

        gross_income = spm_unit("fl_tca_gross_income", period)

        # Compare to 185% FPL (annual FPG converted to monthly)
        fpg = spm_unit("spm_unit_fpg", period)
        gross_income_limit = fpg * p.gross_income_limit_rate

        return gross_income < gross_income_limit
