from policyengine_us.model_api import *


class ks_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-111",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm6410.htm",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7110.htm",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7200.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-110, KEESM 7110, and KEESM 7211:
        # Sum assistance-unit members' earned income after the $90 and 60%
        # deductions, then subtract care expenses. SSI recipients are excluded
        # from the assistance unit (KEESM 4113), so their earnings are not
        # counted.
        #
        # Per KEESM 6410: a child's earned income is exempt as income in the
        # month received, so it is excluded from countable earned income.
        person = spm_unit.members
        is_member = person("ks_tanf_is_assistance_unit_member", period.this_year)
        child_income_exempt = person("ks_tanf_child_earned_income_exempt", period)
        earned_after_deductions = person(
            "ks_tanf_earned_income_after_deductions", period
        )
        counted = is_member & ~child_income_exempt
        countable_earned = spm_unit.sum(earned_after_deductions * counted)
        # Per K.A.R. 30-4-111(b)(3) and KEESM 7211: after the $90 and 60%
        # disregards, deduct reasonable expenses for child care or for the
        # care of an incapacitated person. Kansas applies no dollar cap.
        # KEESM 7211 also requires the cared-for dependent to be in the
        # assistance unit; we don't enforce that, since these expenses are
        # only tracked at the unit level at the moment.
        childcare_expenses = spm_unit("childcare_expenses", period)
        incapacitated_care_expenses = add(spm_unit, period, ["care_expenses"])
        return max_(
            countable_earned - childcare_expenses - incapacitated_care_expenses,
            0,
        )
