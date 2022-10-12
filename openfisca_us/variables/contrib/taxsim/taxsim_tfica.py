from policyengine_us.model_api import *


class taxsim_tfica(Variable):
    value_type = float
    entity = TaxUnit
    label = "Employee share of FICA + SECA + Additional Medicare Tax"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["self_employment_tax", "employee_payroll_tax"])
