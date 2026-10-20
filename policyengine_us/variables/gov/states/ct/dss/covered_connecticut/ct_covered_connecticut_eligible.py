from policyengine_us.model_api import *


class ct_covered_connecticut_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Covered Connecticut Program"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://www.cga.ct.gov/2021/act/pa/pdf/2021PA-00002-R00SB-01202SS1-PA.pdf#page=22",
        # C.G.S. 19a-754c(b)(1)(C)(iv), the codified income limit.
        "https://www.cga.ct.gov/current/pub/chap_368dd.htm#sec_19a-754c",
        "https://portal.ct.gov/dss/health-and-home-care/covered-connecticut-program",
    )
    documentation = (
        "A tax unit is eligible for the Covered Connecticut Program when the "
        "program is in effect, at least one member is eligible for the federal "
        "ACA premium tax credit (which embeds on-Marketplace enrollment, the "
        "married-filing-separately exclusion, and the federal required-"
        "contribution income test), and household ACA MAGI is at or below 175% "
        "of the prior-year federal poverty guideline, measured as the exact "
        "ratio rather than the truncated aca_magi_fraction. Connecticut imposes "
        "no minimum-income "
        "floor: the statutory requirement that enrollees be ineligible for "
        "Medicaid because their income exceeds the Medicaid limits is inherited "
        "from the federal ACA PTC gate, which already excludes Medicaid-eligible "
        "people. The benchmark-silver-enrollment requirement is represented by "
        "using the second-lowest-cost silver plan premium as the modeled "
        "premium in the amount variable, and is not separately gated here. The "
        "statutory eligibility cohorts (adults aged 18 to 64, dependents aged 26 "
        "and under, and parents and caretaker relatives) are deliberately NOT "
        "separately gated, matching sibling state premium-assistance programs, "
        "because the ACA MAGI test and the federal PTC structure already capture "
        "the eligible population."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.covered_connecticut
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC.
        aptc_eligible = tax_unit.any(tax_unit.members("is_aca_ptc_eligible", period))
        # C.G.S. 19a-754c(b)(1)(C)(iv) covers "household income up to one
        # hundred seventy-five per cent of the federal poverty level", which
        # DSS applies "up to an[d] including 175%". Test the exact ratio, not
        # the truncated aca_magi_fraction: truncation maps 175.00%-175.99% to
        # 1.75, which would admit incomes above 175%.
        magi = max_(tax_unit("aca_magi", period), 0)
        exact_magi_frac = magi / tax_unit("tax_unit_fpg", period.last_year)
        income_eligible = exact_magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
