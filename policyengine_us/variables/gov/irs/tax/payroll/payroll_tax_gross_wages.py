from policyengine_us.model_api import *


class payroll_tax_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "Gross wages and salaries for payroll taxes"
    documentation = "Elective deferrals under §401(k)/§403(b) are excluded from income tax wages (Box 1) but included here per IRC §3121(a)."

    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        fica_deductions = person("fica_pre_tax_contributions", period)
        return max_(0, employment_income - fica_deductions)
