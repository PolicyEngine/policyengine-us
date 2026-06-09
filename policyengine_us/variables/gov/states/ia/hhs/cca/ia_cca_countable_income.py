from policyengine_us.model_api import *


class ia_cca_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa CCA countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=4"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.income
        person = spm_unit.members
        # Iowa excludes the earnings of a child age 14 or younger, and the
        # earnings of a child 18 or younger who is a full-time student
        # (IAC 441-170.2(1)"d"(13) and (35)). Both exclusions cover a child's
        # earnings, so they never apply to a tax-unit head or spouse — a
        # teen parent's own wages stay counted. `age` is YEAR-defined, so
        # read the annual value inside this monthly formula.
        age = person("age", period.this_year)
        is_full_time_student = person("is_full_time_student", period.this_year)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        excluded_minor = ~is_head_or_spouse & (
            (age <= p.minor_earnings_age)
            | ((age <= p.minor_student_age) & is_full_time_student)
        )
        wage_income = add(person, period, p.countable_income.earned_sources)
        # A net loss in self-employment income cannot offset other earned or
        # unearned income (IAC 441-170.2(1)"c"(1)), so the per-person
        # self-employment total is floored at zero.
        self_employment = add(
            person, period, p.countable_income.self_employment_sources
        )
        earned_per_person = wage_income + max_(self_employment, 0)
        counted_earned = spm_unit.sum(earned_per_person * ~excluded_minor)
        unearned_income = add(spm_unit, period, p.countable_income.unearned_sources)
        return counted_earned + unearned_income
