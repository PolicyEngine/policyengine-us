from policyengine_us.model_api import *


class pre_c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Personal exemption before phase-out"
    reference = "https://www.law.cornell.edu/uscode/text/26/151"
    unit = USD

    def formula(tax_unit, period, parameters):
        exemption = parameters(period).gov.irs.income.exemption
        return where(
            tax_unit("dsi", period),
            0,
            tax_unit("xtot", period) * exemption.amount,
        )
