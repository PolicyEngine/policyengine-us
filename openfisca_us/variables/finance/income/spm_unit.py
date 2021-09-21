from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class SPM_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit net income"
    definition_period = YEAR


class poverty_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = u"Poverty threshold"
    definition_period = YEAR


class in_poverty(Variable):
    value_type = bool
    entity = SPMUnit
    label = u"In poverty"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("SPM_unit_net_income", period)
        poverty_threshold = spm_unit("poverty_threshold", period)
        return income < poverty_threshold
