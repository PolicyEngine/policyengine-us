from policyengine_us.model_api import *


class excess_withheld_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "excess withheld payroll tax"
    unit = USD
    definition_period = YEAR
