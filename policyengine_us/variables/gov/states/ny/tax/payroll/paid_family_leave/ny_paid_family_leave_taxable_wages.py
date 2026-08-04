from policyengine_us.model_api import *


class ny_paid_family_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "New York paid family leave taxable wages"
    documentation = (
        "Wages subject to New York Paid Family Leave employee contributions, "
        "including federal pre-tax payroll deductions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        return max_(0, person("employment_income", period))
