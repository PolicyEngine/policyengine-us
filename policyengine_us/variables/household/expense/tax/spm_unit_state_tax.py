from policyengine_us.model_api import *


class spm_unit_state_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = "State income tax"
    definition_period = YEAR
    unit = USD

    # state_income_tax is at the tax unit level.
    # sum_of_variables doesn't currently address this case, so write a formula.
    # formula = sum_of_variables(["state_income_tax"])

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        head = person("is_tax_unit_head", period)
        tax = person.tax_unit("state_income_tax", period)
        return spm_unit.sum(head * tax)
