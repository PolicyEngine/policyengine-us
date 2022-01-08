from openfisca_us.model_api import *


class spm_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = u"SPM unit size"
    definition_period = YEAR
