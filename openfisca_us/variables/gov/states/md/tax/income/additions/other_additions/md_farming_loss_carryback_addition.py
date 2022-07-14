## md_farming_loss_carryback_addition.py
from openfisca_us.model_api import *

class md_farming_loss_carryback_addition(Variable):
    # m. Net addition modification to Maryland taxable income when the federal special 2-year carryback (farming loss only) period was used for a net operating loss under federal law compared to Maryland taxable income without regard to federal provisions. Complete and attach Form 500DM.
    value_type = float
    entity = TaxUnit
    label = "MD farming loss carryback"
    documentation = "Net addition modification to Maryland taxable income when the federal special 2-year carryback (farming loss only) period was used for a net operating loss under federal law compared to Maryland taxable income without regard to federal provisions. Complete and attach Form 500DM."
    unit = USD
    definition_period = YEAR