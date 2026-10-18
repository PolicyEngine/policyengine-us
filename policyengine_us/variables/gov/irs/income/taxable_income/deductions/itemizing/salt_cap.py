from policyengine_us.model_api import *


class salt_cap(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT cap"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/164#b_6",
        "https://www.law.cornell.edu/uscode/text/26/164#b_7",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=99",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        max_cap = p.cap[filing_status]
        if p.phase_out.in_effect:
            # 26 U.S.C. 164(b)(7)(B)(iv): modified adjusted gross income adds
            # back income excluded under sections 911, 931 and 933.
            magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
            magi_excess = max_(0, magi - p.phase_out.threshold[filing_status])
            phase_out = p.phase_out.rate * magi_excess
            # 26 USC 164(b)(6)(B) halves a separate filer's applicable
            # limitation amount after 164(b)(7)(B) reduces and floors it; only
            # the threshold is halved first (Schedule A SALT worksheet lines 5
            # and 10). The SEPARATE cap and floor already hold those halves,
            # so the reduction is halved too.
            separate = filing_status == filing_status.possible_values.SEPARATE
            phase_out = where(
                separate, p.phase_out.separate_fraction * phase_out, phase_out
            )
            phased_out_cap = max_(0, max_cap - phase_out)
            if p.phase_out.floor.applies:
                # 164(b)(7)(B)(iii) bars the reduction from taking the cap
                # below the floor; it never raises a cap set below the floor.
                floor = min_(max_cap, p.phase_out.floor.amount[filing_status])
                return max_(phased_out_cap, floor)
            return phased_out_cap
        return max_cap
