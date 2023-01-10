from policyengine_us.model_api import *


class spm_unit_medical_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit medical expenses"
    definition_period = YEAR
    unit = USD

    adds = ["medical_expense"]
