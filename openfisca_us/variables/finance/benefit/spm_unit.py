from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class spm_unit_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit FPG ratio"
    description = "SPM unit's "
    definition_period = YEAR
    def formula(spm_unit, period):
        return spm_unit("spm_unit_net_income", period) / spm_unit(
            "poverty_threshold", period
        )


class children(Variable):
    value_type = int
    entity = SPMUnit
    label = u"children"
    definition_period = YEAR

    def formula(spm_unit, period):
        return spm_unit.sum(spm_unit.members("age", period) < 18)
