from policyengine_us.model_api import *


class me_tanf_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF child care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/C-M-R-10-144-ch-331-IV",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762(3)(B)(7-D):
        # Up to $175/month per child
        # Up to $200/month per child under age 2 or with special needs
        # Per 10-144 CMR ch. 331, Ch. IV, Section B(2)(b), the disregard
        # also covers each incapacitated adult needing care while the
        # recipient works, at the $175 tier.
        p = parameters(period).gov.states.me.dhhs.tanf.child_care

        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)

        # Special needs children get the higher amount (bracket 0 = $200)
        max_per_person = where(
            is_child & is_disabled, p.amount.amounts[0], p.amount.calc(age)
        )

        # Children and incapacitated adults count toward the deduction cap
        care_recipient = is_child | incapacitated_adult
        max_deduction_per_person = max_per_person * care_recipient
        total_max_deduction = spm_unit.sum(max_deduction_per_person)

        # Deduction is lesser of actual expenses or maximum.
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        return min_(childcare_expenses + adult_care_expenses, total_max_deduction)
