from openfisca_us.model_api import *


class pre_c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Personal exemption before phase-out"
    reference = "https://www.law.cornell.edu/uscode/text/26/151"
    unit = USD

    def formula(tax_unit, period, parameters):
        exemption = parameters(period).irs.income.exemption
        return where(
            tax_unit("dsi", period),
            0,
            tax_unit("xtot", period) * exemption.amount,
        )


class exemption_phaseout_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exemption phaseout start"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return parameters(period).irs.income.exemption.phaseout.start[
            tax_unit("mars", period)
        ]


class c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Personal exemptions after phase-out"
    unit = USD

    def formula(tax_unit, period, parameters):
        phaseout = parameters(period).irs.income.exemption.phaseout
        phaseout_start = tax_unit("exemption_phaseout_start", period)
        line_5 = max_(0, tax_unit("c00100", period) - phaseout_start)
        line_6 = line_5 / (2500 / tax_unit("sep", period))
        line_7 = phaseout.rate * line_6
        return tax_unit("pre_c04600", period) * (1 - line_7)
