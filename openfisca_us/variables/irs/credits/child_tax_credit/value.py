from openfisca_us.model_api import *


class child_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Child Tax Credit"
    documentation = "Child tax credit (adjusted) from Form 8812"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/24"

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["ctc_child", "ctc_adult"])
