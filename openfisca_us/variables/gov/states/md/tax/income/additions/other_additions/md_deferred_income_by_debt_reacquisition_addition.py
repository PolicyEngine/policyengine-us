## md_deferred_income_by_debt_reacquisition_addition.py
from openfisca_us.model_api import *

class md_deferred_income_by_debt_reacquisition_addition(Variable):
    # cd. Net addition modification to Maryland taxable income resulting from the federal deferral of income arising from business indebtedness discharged by reacquisition of a debt instrument. See Form 500DM and Administrative Release 38.
    value_type = float
    entity = TaxUnit
    label = "MD deferred income by debt reacquisition"
    documentation = "Net addition modification to Maryland taxable income resulting from the federal deferral of income arising from business indebtedness discharged by reacquisition of a debt instrument. See Form 500DM and Administrative Release 38."
    unit = USD
    definition_period = YEAR