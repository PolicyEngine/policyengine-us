from policyengine_us.model_api import *


class az_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Arizona Child Care Assistance Program countable income"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        # R6-5-4914(F) countable income
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=31",
        # R6-5-4914(G)(13) excluded school-age minor earnings;
        # R6-5-4914(H) child support paid deduction
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=32",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap.income.countable_income
        countable = add(spm_unit, period, p.sources)
        person = spm_unit.members
        # R6-5-4914(G)(13): exclude the earnings of a child under 18 attending
        # high school / training who is not a minor parent. Minor parents are the
        # head/spouse of their own tax unit, so only non-head/spouse minor students
        # are excluded here.
        age = person("age", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_excluded_minor = (age < 18) & is_student & ~is_head_or_spouse
        minor_earnings = (
            person("employment_income", period)
            + person("self_employment_income", period)
            + person("sstb_self_employment_income", period)
            + person("farm_operations_income", period)
        ) * is_excluded_minor
        excluded_minor_earnings = spm_unit.sum(minor_earnings)
        # R6-5-4914(H): deduct legally mandated child support paid for dependents
        # residing outside the household.
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        net = max_(countable - excluded_minor_earnings - child_support_paid, 0)
        # R6-5-4914(I): use the whole-dollar amount only, rounded down.
        return np.floor(net)
