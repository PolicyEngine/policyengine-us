from openfisca_us.model_api import *


class c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Personal exemptions after phase-out"
    unit = USD

    def formula(tax_unit, period, parameters):
        phase_out = parameters(period).gov.irs.income.exemption.phase_out
        phase_out_start = tax_unit("exemption_phase_out_start", period)
        line_5 = max_(
            0, tax_unit("adjusted_gross_income", period) - phase_out_start
        )
        line_6 = line_5 / (2500 / tax_unit("sep", period))
        line_7 = phase_out.rate * line_6
        return tax_unit("pre_c04600", period) * (1 - line_7)
