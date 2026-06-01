from policyengine_us.model_api import *


class ny_disability_benefits_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "New York disability benefits taxable wages"
    documentation = (
        "Wages subject to New York Disability Benefits employee withholding, "
        "including federal pre-tax payroll deductions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        return max_(0, person("employment_income", period))
