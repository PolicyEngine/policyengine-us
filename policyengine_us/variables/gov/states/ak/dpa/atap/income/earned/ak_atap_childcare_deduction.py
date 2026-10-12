from policyengine_us.model_api import *


class ak_atap_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP childcare deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.485"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Per 7 AAC 45.485(a)(2): care costs excluded up to:
        # - $200/month per child under age 2
        # - $175/month per child age 2 and older
        # - $175/month for an incapacitated parent whose needs are
        #   included in the ATAP determination (subsection (a)(2)(C))
        p = parameters(period).gov.states.ak.dpa.atap.income.deductions
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        incapacitated_parent = person("is_tax_unit_head_or_spouse", period) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("age", period.this_year)
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        care_recipient = dependent | incapacitated_parent
        max_per_person = p.childcare.calc(age) * care_recipient
        total_max_disregard = spm_unit.sum(max_per_person)
        return min_(childcare_expenses + adult_care_expenses, total_max_disregard)
