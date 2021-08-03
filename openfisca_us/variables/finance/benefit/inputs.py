from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class gross_income(Variable):
    value_type = float
    entity = BenefitUnit
    label = u"Income before SNAP program deductions are applied"
    definition_period = YEAR


class net_income(Variable):
    value_type = float
    entity = BenefitUnit
    label = u"Income after SNAP program deductions are applied"
    definition_period = YEAR


class people(Variable):
    value_type = int
    entity = BenefitUnit
    label = u"Number of individuals in a BenefitUnit"
    definition_period = YEAR
