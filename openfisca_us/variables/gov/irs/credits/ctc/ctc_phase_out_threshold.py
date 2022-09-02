from openfisca_us.model_api import *


class ctc_phase_out_threshold(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC phase-out threshold"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).irs.credits.ctc
        filing_status = tax_unit("filing_status", period)
        return ctc.phaseout.threshold[filing_status]
