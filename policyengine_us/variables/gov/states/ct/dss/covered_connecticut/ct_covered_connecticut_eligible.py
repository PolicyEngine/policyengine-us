from policyengine_us.model_api import *


class ct_covered_connecticut_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Covered Connecticut Program"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://www.cga.ct.gov/2021/act/pa/pdf/2021PA-00002-R00SB-01202SS1-PA.pdf#page=21",
        "https://portal.ct.gov/dss/health-and-home-care/covered-connecticut-program",
    )
    documentation = (
        "A tax unit is eligible for the Covered Connecticut Program when the "
        "program is in effect, at least one member is eligible for the federal "
        "ACA premium tax credit (which embeds on-Marketplace enrollment, the "
        "married-filing-separately exclusion, and the federal required-"
        "contribution income test), and household ACA MAGI is at or below 175% "
        "of the federal poverty line. Connecticut imposes no minimum-income "
        "floor: the statutory requirement that enrollees be ineligible for "
        "Medicaid because their income exceeds the Medicaid limits is inherited "
        "from the federal ACA PTC gate, which already excludes Medicaid-eligible "
        "people. The benchmark-silver-enrollment requirement is represented by "
        "using the second-lowest-cost silver plan premium as the modeled "
        "premium in the amount variable, and is not separately gated here. No "
        "explicit age gate (18-64, or dependents 26 and under) is applied, "
        "matching sibling state premium-assistance programs, because the "
        "MAGI and federal PTC structure captures the population."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.covered_connecticut
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC.
        aptc_eligible = tax_unit.any(tax_unit.members("is_aca_ptc_eligible", period))
        income_eligible = tax_unit("aca_magi_fraction", period) <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
