from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ks_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Kansas TANF gross income eligible"
    definition_period = MONTH
    reference = (
        "https://ksrevisor.gov/statutes/chapters/ch39/039_007_0009.html",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm6410.htm",
        "https://www.dcf.ks.gov/services/ees/Documents/Reports/TANF%20State%20Plan%20FFY%202024%20-%202026.pdf",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.S.A. 39-709 and Kansas TANF State Plan:
        # Gross income must be less than 30% of the Federal Poverty Level. SSI
        # recipients are excluded from the assistance unit (KEESM 4113), so
        # they are left out of both the counted income and the poverty-
        # guideline household size used for the threshold.
        #
        # Per KEESM 6410: a child's earned income is exempt as income, so it is
        # excluded from the gross-income test.
        person = spm_unit.members
        is_member = person("ks_tanf_is_assistance_unit_member", period.this_year)
        child_income_exempt = person("ks_tanf_child_earned_income_exempt", period)
        earned = person("tanf_gross_earned_income", period) * ~child_income_exempt
        unearned = person("tanf_gross_unearned_income", period)
        gross_income = spm_unit.sum((earned + unearned) * is_member)
        size = spm_unit("ks_tanf_assistance_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        monthly_fpg = fpg(size, state_group, period, parameters) / MONTHS_IN_YEAR
        p = parameters(period).gov.states.ks.dcf.tanf.income
        return gross_income < monthly_fpg * p.gross_income_limit
