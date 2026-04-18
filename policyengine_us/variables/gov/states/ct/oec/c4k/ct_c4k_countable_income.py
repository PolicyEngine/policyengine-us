from policyengine_us.model_api import *


class ct_c4k_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Connecticut Care 4 Kids countable income"
    reference = "https://eregulations.ct.gov/eRegsPortal/Browse/RCSA/Title_17bSubtitle_17b-749Section_17b-749-05/"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.oec.c4k.income
        # Per RCSA 17b-749-05(b)(2)(E), "the earnings of a family member
        # who is under the age of eighteen who is not the parent of a
        # child for whom assistance is requested" are excluded from
        # countable income. Sum earned income sources only for members
        # aged 18+ or who are the tax-unit head/spouse (covering the
        # edge case of a teen parent whose earnings remain countable).
        # Unearned income is summed across all members per
        # 17b-749-05(b)(1)(A) ("unearned income of all adult and child
        # family members").
        person = spm_unit.members
        # `age` is YEAR-defined; use period.this_year to read the annual
        # value rather than age/12 in a monthly formula.
        is_adult = person("age", period.this_year) >= 18
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        earnings_counted = is_adult | is_parent
        earned_per_person = sum(person(source, period) for source in p.earned_sources)
        earned_income = spm_unit.sum(earned_per_person * earnings_counted)
        unearned_income = add(spm_unit, period, p.unearned_sources)
        deductions = add(spm_unit, period, p.deductions)
        return max_(earned_income + unearned_income - deductions, 0)
