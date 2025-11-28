from policyengine_us.model_api import *


class payroll_tax_revenue_medicare(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Medicare payroll tax revenue"
    documentation = "Medicare HI payroll tax revenue from employee and employer contributions and additional Medicare tax"
    unit = USD

    def formula(person, period, parameters):
        return add(
            person,
            period,
            ["employee_medicare_tax", "employer_medicare_tax"],
        ) + person.tax_unit("additional_medicare_tax", period)
