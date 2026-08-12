from policyengine_us.model_api import *


class ok_ccs_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Oklahoma Child Care Subsidy adjusted monthly income"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = (
        "https://okrules.elaws.us/oac/340:40-7-12",
        "https://okrules.elaws.us/oac/340:40-7-13",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.income
        gross_income = spm_unit("ok_ccs_gross_income", period)
        # The earned income of a child under 18 years of age who attends
        # school regularly is excluded (OAC 340:40-7-12). School attendance is
        # not tracked, so age alone drives the exclusion; the head-or-spouse
        # guard keeps a minor parent's own wages countable.
        person = spm_unit.members
        is_minor = person("age", period.this_year) < p.child_earned_income_exclusion_age
        not_head_or_spouse = ~person("is_tax_unit_head_or_spouse", period.this_year)
        minor_earned_income = spm_unit.sum(
            (is_minor & not_head_or_spouse)
            * person("ok_ccs_countable_earned_income", period)
        )
        # Verified, legally binding child support paid by a household member to
        # or for a non-household member is deducted (OAC 340:40-7-13).
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        adjusted_income = max_(
            gross_income - minor_earned_income - child_support_paid, 0
        )
        # The adjusted monthly income is rounded to the nearest dollar before
        # the Appendix C-4 threshold and copayment lookups, with half dollars
        # rounding up; np.round would round them to the even dollar.
        return np.floor(adjusted_income + 0.5)
