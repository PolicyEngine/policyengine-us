from policyengine_us.model_api import *


class md_premium_assistance_young_adult_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Premium Assistance young adult contribution percentage reduction"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MD
    # COMAR 14.35.19.04B (Young Adult Subsidy) defines the age-based
    # reduction per enrollee; codified COMAR chapter 14.35.21 governs the
    # State-Based Health Insurance Subsidies Program.
    reference = (
        "https://www.marylandhbe.com/wp-content/uploads/2025/07/Final-2026-State-Subsidy-and-Reinsurance-Parameters-Board-7-21-25-1.pdf#page=14",
        "https://regs.maryland.gov/us/md/exec/comar/14.35.21#page=6",
    )
    # Young Adult Subsidy overlay reduces the tax unit's target contribution
    # percentage. COMAR 14.35.19.04B defines the reduction per enrollee, and
    # no source states how to combine enrollees of different ages within one
    # tax unit. This variable applies the most generous reduction among the
    # unit's federally APTC-eligible members at the tax-unit level, which is a
    # unit-wide APPROXIMATION: it is exact for single-enrollee units but
    # over-grants for mixed-age multi-enrollee units. It is not restructured
    # to a per-enrollee calculation here.
    #
    # The YAS Medicaid-ineligibility floor is satisfied via
    # is_aca_ptc_eligible below, since APTC eligibility excludes those
    # eligible for Medicaid.

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.mhbe.premium_assistance
        age = tax_unit.members("age", period)
        person_reduction = p.young_adult.reduction.calc(age)
        # Only enrollees eligible for the federal APTC receive the subsidy,
        # so only their ages can drive the tax unit's reduction.
        is_enrollee = tax_unit.members("is_aca_ptc_eligible", period)
        return tax_unit.max(where(is_enrollee, person_reduction, 0))
