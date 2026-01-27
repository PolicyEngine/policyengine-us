from policyengine_us.model_api import *


class va_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF childcare deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=56"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.va.dss.tanf.income.deductions.dependent_care
        person = spm_unit.members
        age = person("age", period.this_year)
        dependent = person("is_tax_unit_dependent", period)
        disabled_adult = person("is_adult", period) & person(
            "is_disabled", period.this_year
        )
        care_recipient = dependent | disabled_adult
        childcare_expenses = spm_unit("childcare_expenses", period)
        max_deduction = spm_unit.sum(p.full_time.calc(age) * care_recipient)
        return min_(childcare_expenses, max_deduction)
