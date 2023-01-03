from policyengine_us.model_api import *


class ctc_arpa_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Phase-out of CTC ARPA addition"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return min_(
            tax_unit("ctc_arpa_phase_out_cap", period),
            tax_unit("ctc_arpa_uncapped_phase_out", period),
        )
