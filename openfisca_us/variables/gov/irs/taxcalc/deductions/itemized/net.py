from openfisca_us.model_api import *


class c21040(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Phased-out itemized deductions"
    unit = USD
    documentation = "Itemized deductions that are phased out"


class c04470(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Itemized deductions after phase-out"
    unit = USD
    documentation = (
        "Itemized deductions after phase-out (zero for non-itemizers)"
    )

    def formula(tax_unit, period, parameters):
        return max_(0, tax_unit("c21060", period) - tax_unit("c21040", period))
