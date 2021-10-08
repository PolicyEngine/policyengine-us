from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.entity.household import *  # not sure what I need here


class gross_income(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation = "income before adjustments for SNAP household"


class number_of_individuals(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation = "number of individuals in the household"


class housing_cost(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation = "monthly housing cost for the household"


class disabled_or_elderly_in_household(Variable):
    value_type = bool
    entity = household
    definition_period = YEAR
    documentation = "flag to indicate presence of disabled or elderly (age >= 60, per USDA), in household"


class elderly_or_disabled_medical_expenses(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation = "out-of-pocket medical expenses for disabled and/or elderly individuals"
