from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class spm_unit_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit FPG"
    description = "SPM unit's federal poverty guideline"
    definition_period = YEAR

    def formula(spm_unit, period):
        # Parameters
        # Get state group and spm unit size.
        