from policyengine_us.model_api import *


class cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC credit rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#a_2"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.cdcc
        agi = tax_unit("adjusted_gross_income", period)

        # First phase-out
        excess_agi = max_(0, agi - p.phase_out.start)
        increments = np.ceil(excess_agi / p.phase_out.increment)
        percentage_reduction = increments * p.phase_out.rate
        phased_out_rate = max_(
            p.phase_out.min, p.phase_out.max - percentage_reduction
        )

        # Second phase-out
        second_excess_agi = max_(0, agi - p.phase_out.second_start)
        second_increments = np.ceil(second_excess_agi / p.phase_out.increment)
        second_percentage_reduction = second_increments * p.phase_out.rate
        if p.phase_out.amended_structure.applies:
            # Second phase-out is amended post 2025
            filing_status = tax_unit("filing_status", period)
            second_phase_out_start = (
                p.phase_out.amended_structure.second_start[filing_status]
            )
            second_excess_agi = max_(0, agi - second_phase_out_start)
            second_phase_out_increment = (
                p.phase_out.amended_structure.second_increment[filing_status]
            )
            second_increments = np.ceil(
                second_excess_agi / second_phase_out_increment
            )
            second_percentage_reduction = second_increments * p.phase_out.rate
            return max_(
                p.phase_out.amended_structure.second_min,
                phased_out_rate - second_percentage_reduction,
            )
        return max_(0, phased_out_rate - second_percentage_reduction)
