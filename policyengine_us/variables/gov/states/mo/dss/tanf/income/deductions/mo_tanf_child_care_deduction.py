from policyengine_us.model_api import *


class mo_tanf_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF child care cost deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.child_care_deduction
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        # Per 13 CSR 40-2.120(6)(A)5, the disregard also covers care of an
        # incapacitated individual living in the same home as the dependent
        # child, at the $175 age-two-or-older tier.
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("age", period.this_year)
        # Children use their age-based rate; the older-age zero-out reflects
        # children aging out of care. An incapacitated adult instead receives
        # the standard age-two-or-older rate ($175), so evaluate the schedule
        # at the age-two boundary for them.
        cap_age = where(incapacitated_adult, p.amount.thresholds[1], age)
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        care_recipient = dependent | incapacitated_adult
        max_deduction_per_person = p.amount.calc(cap_age) * care_recipient
        total_max_deduction = spm_unit.sum(max_deduction_per_person)
        return min_(childcare_expenses + adult_care_expenses, total_max_deduction)
