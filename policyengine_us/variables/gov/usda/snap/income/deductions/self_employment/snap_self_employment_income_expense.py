from policyengine_us.model_api import *


class snap_self_employment_income_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "All self-employment income expenses for the SNAP self-employment deduction"
    unit = USD
    definition_period = YEAR


# Each state defines deductible self-employment income expenses for SNAP.
# E.g. see Mississippi: https://www.law.cornell.edu/regulations/mississippi/18-Miss-Code-R-SS-14-20-4
# The relevant expenses are often linked to TANF self-employment income expenses.
