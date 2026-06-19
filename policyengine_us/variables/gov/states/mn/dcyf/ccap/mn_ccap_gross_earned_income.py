from policyengine_us.model_api import *


class mn_ccap_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Minnesota CCAP gross earned income"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.06",
        "https://www.revisor.mn.gov/rules/3400.0170/",
    )

    def formula(spm_unit, period, parameters):
        # Earned income is counted gross, before payroll deductions, excluding a
        # child's earned income. Section 6.6.1 also counts a non-student minor's
        # and a dependent student's earnings, which we don't separately track.
        p = parameters(period).gov.states.mn.dcyf.ccap.income.countable_income
        person = spm_unit.members
        wages = add(person, period, p.earned)
        # Minn. Rules 3400.0170, subp. 4 and CCAP Policy Manual section 6.15.6:
        # a net self-employment loss may offset self-employment income from
        # another business but cannot reduce wages, so floor the per-person
        # self-employment total at zero before adding it to wages.
        self_employment = add(person, period, p.self_employment_sources)
        earned = wages + max_(self_employment, 0)
        is_child = person("is_child", period)
        return spm_unit.sum(earned) - spm_unit.sum(earned * is_child)
