from policyengine_us.model_api import *


class ca_cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC credit rate replicated to include California limitations"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631",
        "https://www.ftb.ca.gov/forms/2025/2025-3506-instructions.html",  # Line 7
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.6",  # (a)(1)
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        year = period.start.year
        if year != 2021:
            # R&TC 17052.6(a)(1) ties the credit to IRC 21 "as applicable for
            # federal income tax purposes for the taxable year", which
            # overrides the R&TC 17024.5 specified date. So outside 2021,
            # FTB 3506 line 7 uses the federal decimal table for the same
            # year, including the 2026 schedule of P.L. 119-21.
            return tax_unit("cdcc_rate", period)

        # California did not adopt the 2021 American Rescue Plan Act rate,
        # so 2021 uses the 2020 schedule.
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(f"{year - 1}-01-01").gov.irs.credits.cdcc

        # First phase-out
        excess_agi = max_(0, agi - p.phase_out.start)  # start
        increments = np.ceil(excess_agi / p.phase_out.increment)
        percentage_reduction = increments * p.phase_out.rate
        phased_out_rate = max_(
            p.phase_out.min,
            p.phase_out.max - percentage_reduction,  # max
        )

        # Second phase-out
        second_excess_agi = max_(0, agi - p.phase_out.second_start)  # second_start
        second_increments = np.ceil(second_excess_agi / p.phase_out.increment)
        second_percentage_reduction = second_increments * p.phase_out.rate

        return max_(0, phased_out_rate - second_percentage_reduction)
