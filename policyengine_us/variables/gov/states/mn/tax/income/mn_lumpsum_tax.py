from policyengine_us.model_api import *


class mn_lumpsum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota lump-sum tax"
    unit = USD
    definition_period = YEAR
    reference = (
    )
    defined_for = StateCode.MN

    # def formula(tax_unit, period, parameters):
