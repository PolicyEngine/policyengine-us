from policyengine_us.model_api import *


class mt_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/tanf602-1jan012018.pdf#page=1"
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf.income.deductions.dependent_care
        person = spm_unit.members

        is_dependent = person("is_tax_unit_dependent", period.this_year)
        is_child = person("mt_tanf_eligible_child", period)
        is_adult = person("is_adult", period.this_year)
        is_incapable_of_self_care = person(
            "is_incapable_of_self_care", period.this_year
        )
        # Mont. Admin. r. 37.78.406(2)(c) imposes no dependency requirement
        # on the incapacitated adult, so an incapacitated spouse qualifies.
        is_eligible_person = (is_dependent & is_child) | (
            is_adult & is_incapable_of_self_care
        )

        # Per TANF manual 602-1, the disregard covers care for each minor
        # child or incapacitated adult, so adult care expenses count too.
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        dependent_deduction_person = p.amount * is_eligible_person
        total_dependent_deduction = spm_unit.sum(dependent_deduction_person)

        return min_(
            childcare_expenses + adult_care_expenses,
            total_dependent_deduction,
        )
