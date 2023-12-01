from policyengine_us.model_api import *


class ca_cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC credit rate replicated to include California limitations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631"
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)

        year = period.start.year
        if year == 2021:
            period_adjusted = f"{year-1}-01-01"
        else:
            period_adjusted = f"{year}-01-01"

        p = parameters(period_adjusted).gov.irs.credits.cdcc

        # First phase-out
        excess_agi = max_(0, agi - p.phase_out.start)  # start
        increments = np.ceil(excess_agi / p.phase_out.increment)
        percentage_reduction = increments * p.phase_out.rate
        phased_out_rate = max_(
            p.phase_out.min, p.phase_out.max - percentage_reduction  # max
        )

        # Second phase-out
        second_excess_agi = max_(
            0, agi - p.phase_out.second_start
        )  # second_start
        second_increments = np.ceil(second_excess_agi / p.phase_out.increment)
        second_percentage_reduction = second_increments * p.phase_out.rate

        return max_(0, phased_out_rate - second_percentage_reduction)
