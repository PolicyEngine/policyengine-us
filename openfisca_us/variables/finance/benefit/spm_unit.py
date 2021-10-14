from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class state_group(Variable):
    value_type = str
    entity = SPMUnit
    label = u"state_group"
    definition_period = YEAR


class poverty_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = u"poverty_ratio"
    definition_period = YEAR


class children(Variable):
    value_type = int
    entity = SPMUnit
    label = u"children"
    definition_period = YEAR
