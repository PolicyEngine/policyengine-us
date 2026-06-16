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
        earned = add(person, period, p.earned)
        is_child = person("is_child", period)
        return spm_unit.sum(earned) - spm_unit.sum(earned * is_child)
