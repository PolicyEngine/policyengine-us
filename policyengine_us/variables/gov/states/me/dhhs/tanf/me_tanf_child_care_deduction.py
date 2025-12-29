from policyengine_us.model_api import *


class me_tanf_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF child care deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html"
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762(3)(B)(7-D):
        # Up to $175/month per child
        # Up to $200/month per child under age 2 or with special needs
        p = parameters(period).gov.states.me.dhhs.tanf.child_care

        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)

        # Determine max deduction per child based on age and disability
        is_infant_or_special_needs = (
            age < p.infant_age_threshold
        ) | is_disabled
        max_per_child = where(
            is_infant_or_special_needs,
            p.infant_or_special_needs_max,
            p.standard_max,
        )

        # Only children count toward the deduction cap
        max_deduction_per_person = max_per_child * is_child
        total_max_deduction = spm_unit.sum(max_deduction_per_person)

        # Deduction is lesser of actual expenses or maximum
        childcare_expenses = spm_unit("childcare_expenses", period)
        return min_(childcare_expenses, total_max_deduction)
