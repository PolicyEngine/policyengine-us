from policyengine_us.model_api import *


class ks_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Kansas TANF gross income eligible"
    definition_period = MONTH
    reference = (
        "https://ksrevisor.gov/statutes/chapters/ch39/039_007_0009.html",
        "https://www.dcf.ks.gov/services/ees/Documents/Reports/TANF%20State%20Plan%20FFY%202024%20-%202026.pdf",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.S.A. 39-709 and Kansas TANF State Plan:
        # Gross income must be less than 30% of Federal Poverty Level
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )
        fpg = spm_unit("spm_unit_fpg", period)
        p = parameters(period).gov.states.ks.dcf.tanf.income
        return gross_income < fpg * p.gross_income_limit
