from policyengine_us.model_api import *


class va_ccsp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Virginia Child Care Subsidy Program countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section40/",
        "https://doe.virginia.gov/home/showpublisheddocument/56270#page=63",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.ccsp.income.countable_income
        # Per 8VAC20-790-40(H), earnings of a family member younger than 18
        # years of age are excluded from countable income. We sum earned
        # income (wages and self-employment) for adult (18+) members only,
        # and sum unearned income across all members.
        person = spm_unit.members
        # `age` is a YEAR-defined variable; use period.this_year so the
        # monthly formula picks up the annual age rather than age/12.
        is_adult = person("age", period.this_year) >= 18
        earned_per_person = sum(person(source, period) for source in p.earned_sources)
        adult_earned_income = spm_unit.sum(earned_per_person * is_adult)
        unearned_income = add(spm_unit, period, p.unearned_sources)
        deductions = add(spm_unit, period, p.subtracts)
        return adult_earned_income + unearned_income - deductions
