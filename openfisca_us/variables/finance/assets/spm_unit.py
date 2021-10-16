from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class spm_unit_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit assets"
    definition_period = YEAR
