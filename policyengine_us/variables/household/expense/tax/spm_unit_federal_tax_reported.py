from policyengine_us.model_api import *


class spm_unit_federal_tax_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "Federal income tax (reported"
    definition_period = YEAR
    unit = USD
