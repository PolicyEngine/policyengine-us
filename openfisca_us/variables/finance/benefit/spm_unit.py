from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class poverty_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = u"poverty_ratio"
    definition_period = YEAR

    def formula(spm_unit, period):
        return spm_unit("SPM_unit_net_income", period) / spm_unit(
            "poverty_threshold", period
        )


class children(Variable):
    value_type = int
    entity = SPMUnit
    label = u"children"
    definition_period = YEAR

    def formula(spm_unit, period):
        return spm_unit.sum(spm_unit.members("age", period) < 18)
