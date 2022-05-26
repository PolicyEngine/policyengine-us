from openfisca_us.model_api import *


class cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC credit rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#a_2"

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.cdcc
        agi = tax_unit("adjusted_gross_income", period)

        # First phase-out
        phase_out_agi = max_(0, agi - cdcc.phaseout.start)
        percentage_reduction = np.ceil(cdcc.phaseout.rate * phase_out_agi)
        phased_out_rate = max_(
            cdcc.phaseout.min, cdcc.phaseout.max - percentage_reduction
        )

        # Second phase-out
        second_phase_out_agi = max_(0, agi - cdcc.phaseout.second_start)
        second_percentage_reduction = np.ceil(
            cdcc.phaseout.rate * second_phase_out_agi
        )
        return max_(0, phased_out_rate - second_percentage_reduction)
