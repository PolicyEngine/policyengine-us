from policyengine_us.model_api import *


class state_payroll_tax_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "state payroll tax gross wages"
    documentation = (
        "Gross employment wages used by state payroll taxes and contributions "
        "that include federal pre-tax payroll deductions in their wage base."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return max_(0, person("employment_income", period))
