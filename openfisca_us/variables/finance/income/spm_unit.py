from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class SPM_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit net income"
    definition_period = YEAR
