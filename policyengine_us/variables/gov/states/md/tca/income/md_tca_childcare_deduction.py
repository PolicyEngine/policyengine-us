from policyengine_us.model_api import *


class md_tca_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA childcare deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-03-13"

    def formula(spm_unit, period, parameters):
        # Per COMAR 07.03.03.13.E(3)(c), the deduction covers payments for
        # the care of each child in the assistance unit or an incapacitated
        # adult living in the home, capped at actual expenses, "not to
        # exceed" per person based on employment hours: $200 for 100+
        # hours/month, $100 for <100 hours.
        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        num_care_recipients = spm_unit.sum(is_child | incapacitated_adult)
        monthly_hours = person("monthly_hours_worked", period.this_year)
        max_monthly_hours = spm_unit.max(monthly_hours)
        p = parameters(period).gov.states.md.tca.income.deductions
        # Maximum deduction per care recipient based on monthly work hours
        per_person_cap = p.childcare_expenses.cap.calc(max_monthly_hours)
        max_deduction = per_person_cap * num_care_recipients
        # Actual care expenses (capped at regulatory maximum).
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        return min_(childcare_expenses + adult_care_expenses, max_deduction)
