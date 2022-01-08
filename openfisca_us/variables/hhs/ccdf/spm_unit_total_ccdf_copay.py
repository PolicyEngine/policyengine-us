from openfisca_us.model_api import *


class spm_unit_total_ccdf_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = u"SPM unit total CCDF copay"
    unit = "currency-USD"
