from policyengine_us.model_api import *


class de_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://archive.regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/Delaware%20Social%20Services%20Manual/4000.pdf#page=6",
        "https://help.workworldapp.com/wwwebhelp/de_earned_income_disregards_tanf_and_ga.htm",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4004.2(4): Dependent care as paid up to $200/month per
        # dependent child under age 2 and up to $175/month per dependent
        # child or incapacitated adult living in the home and receiving
        # TANF.
        p = parameters(period).gov.states.de.dhss.tanf.income.deductions

        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("monthly_age", period)

        # Calculate maximum deduction per care recipient based on age
        care_recipient = is_dependent | incapacitated_adult
        max_per_person = p.dependent_care.calc(age)
        total_max = spm_unit.sum(max_per_person * care_recipient)

        # Cap at actual care expenses.
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])

        return min_(childcare_expenses + adult_care_expenses, total_max)
