from policyengine_us.model_api import *


class health_savings_account_payroll_contributions(Variable):
    value_type = float
    entity = Person
    # Separate from health_savings_account_ald which are not made through
    # payroll deductions.
    label = "Health Savings Account payroll contributions"
    unit = USD
    definition_period = YEAR
