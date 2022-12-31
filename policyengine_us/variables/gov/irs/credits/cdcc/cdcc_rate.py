from policyengine_us.model_api import *


class cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC credit rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#a_2"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        pgov = parameters(period).gov
        taxsim_emulation = pgov.contrib.nber.taxsim35_emulation
        pcdcc = pgov.irs.credits.cdcc
        phase_out_increment = pcdcc.phase_out.increment
        phase_out_rate = pcdcc.phase_out.rate
        phase_out_min = pcdcc.phase_out.min
        phase_out_max = pcdcc.phase_out.max
        # first phase-out
        excess_agi = max_(0, agi - pcdcc.phase_out.start)
        if taxsim_emulation:
            increments = excess_agi / phase_out_increment
        else:
            increments = np.ceil(excess_agi / phase_out_increment)
        reduction = increments * phase_out_rate
        phased_out_rate = max_(phase_out_min, phase_out_max - reduction)
        if taxsim_emulation:
            phased_out_rate = where(
                (phased_out_rate - phase_out_min) < 0.01,
                phase_out_min,
                phased_out_rate
            )
        # second phase-out
        excess_agi = max_(0, agi - pcdcc.phase_out.second_start)
        if taxsim_emulation:
            increments = excess_agi / phase_out_increment
        else:
            increments = np.ceil(excess_agi / phase_out_increment)
        reduction = increments * phase_out_rate
        return max_(0, phased_out_rate - reduction)
