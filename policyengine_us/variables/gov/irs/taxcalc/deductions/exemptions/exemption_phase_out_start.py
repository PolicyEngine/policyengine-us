from policyengine_us.model_api import *


class exemption_phase_out_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exemption phase-out start"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return parameters(period).gov.irs.income.exemption.phase_out.start[
            tax_unit("filing_status", period)
        ]
