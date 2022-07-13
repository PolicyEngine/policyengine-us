## md_decoupled_depreciation_allowances_addition.py
from openfisca_us.model_api import *

class md_decoupled_depreciation_allowances_addition(Variable):
    # l. Net addition modification to Maryland taxable income when claiming the federal depreciation allowances from which the State of Maryland has decoupled. Complete and attach Form 500DM. See Administrative Release 38.
    value_type = float
    entity = TaxUnit
    label = "MD decoupled depreciation allowances"
    documentation = "Net addition modification to Maryland taxable income when claiming the federal depreciation allowances from which the State of Maryland has decoupled. Complete and attach Form 500DM. See Administrative Release 38."
    unit = USD
    definition_period = YEAR