from policyengine_us.model_api import *


class fl_tca_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA gross income eligible"
    definition_period = MONTH
    reference = (
        "https://flrules.org/gateway/RuleNo.asp?id=65A-4.220",
        "https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per FAC 65A-4.220: Gross income (after $90 per earner deduction) < 185% FPL
        p = parameters(period).gov.states.fl.dcf.tanf.income.gross_test

        # Apply $90 deduction per person with earned income
        person = spm_unit.members
        earned = person("tanf_gross_earned_income", period)
        deduction = p.earned_deduction
        # Each earner gets $90 deducted (applied only to those with earnings)
        has_earnings = earned > 0
        adjusted_earned = max_(earned - deduction, 0) * has_earnings
        total_adjusted_earned = spm_unit.sum(adjusted_earned)

        # Add gross unearned income (no deduction)
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        adjusted_gross_income = total_adjusted_earned + gross_unearned

        # Compare to 185% FPL (annual FPG converted to monthly)
        fpg = spm_unit("spm_unit_fpg", period.this_year)
        monthly_fpg = fpg / MONTHS_IN_YEAR
        gross_income_limit = monthly_fpg * p.fpl_percent

        return adjusted_gross_income < gross_income_limit
