from policyengine_us.model_api import *


class cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC credit rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#a_2"

    def formula(tax_unit, period, parameters):
        pgov = parameters(period).gov
        taxsim_emulation = pgov.contrib.nber.taxsim35_emulation
        pcdcc = pgov.irs.credits.cdcc
        agi = tax_unit("adjusted_gross_income", period)
        # first phase-out
        excess_agi = max_(0, agi - pcdcc.phase_out.start)
        if taxsim_emulation:
            increments = excess_agi / pcdcc.phase_out.increment
        else:
            increments = np.ceil(excess_agi / pcdcc.phase_out.increment)
        pct_reduction = increments * pcdcc.phase_out.rate
        phased_out_rate = max_(
            pcdcc.phase_out.min, pcdcc.phase_out.max - pct_reduction
        )
        # second phase-out
        excess_agi = max_(0, agi - pcdcc.phase_out.second_start)
        increments = np.ceil(excess_agi / pcdcc.phase_out.increment)
        pct_reduction = increments * pcdcc.phase_out.rate
        return max_(0, phased_out_rate - pct_reduction)
