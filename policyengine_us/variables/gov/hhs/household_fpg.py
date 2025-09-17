from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class household_fpg(Variable):
    value_type = float
    entity = Household
    label = "Household's federal poverty guideline"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        n = household("household_size", period)
        state_group = household("state_group_str", period)
        return fpg(n, state_group, period, parameters)