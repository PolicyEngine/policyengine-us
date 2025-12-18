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
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        gross_income = gross_earned + gross_unearned
        # Get FPL for family size
        family_size = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        p_fpg = parameters(period).gov.hhs.fpg
        # Calculate monthly FPL
        fpg_first = p_fpg.first_person[state_group] / MONTHS_IN_YEAR
        fpg_additional = p_fpg.additional_person[state_group] / MONTHS_IN_YEAR
        monthly_fpg = fpg_first + (family_size - 1) * fpg_additional
        # Apply 30% threshold
        p = parameters(period).gov.states.ks.dcf.tanf.gross_income_limit
        threshold = monthly_fpg * p.rate
        return gross_income < threshold
