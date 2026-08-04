from policyengine_us.model_api import *


class il_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Illinois Temporary Assistance for Needy Families (TANF) child care deduction "
    )
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.143"  # (b)(2)
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.income.child_care_deduction
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        # Per 89 Ill. Adm. Code 112.143(b)(1)(C), care of an incapacitated
        # adult is an exception to direct payment and flows through the
        # care deduction at the age-two-or-older tier.
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("monthly_age", period)
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        care_recipient = dependent | incapacitated_adult
        care_deduction_person = p.calc(age) * care_recipient
        total_care_deduction = spm_unit.sum(care_deduction_person)

        return min_(childcare_expenses + adult_care_expenses, total_care_deduction)
