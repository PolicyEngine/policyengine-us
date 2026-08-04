from policyengine_us.model_api import *


class md_premium_assistance_young_adult_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Premium Assistance young adult contribution percentage reduction"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://www.marylandhbe.com/wp-content/uploads/2025/07/Final-2026-State-Subsidy-and-Reinsurance-Parameters-Board-7-21-25-1.pdf#page=14",
        "https://mgaleg.maryland.gov/pubs/committee/AELR/25-134E-Regulation.pdf#page=3",
    )
    documentation = (
        "Young Adult Subsidy overlay reduces the tax unit's target "
        "contribution percentage. The reduction is age-based per enrollee; "
        "the most generous reduction among the tax unit's federally "
        "APTC-eligible members applies at the tax unit level."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.mhbe.premium_assistance
        age = tax_unit.members("age", period)
        person_reduction = p.young_adult.reduction.calc(age)
        # Only enrollees eligible for the federal APTC receive the subsidy,
        # so only their ages can drive the tax unit's reduction.
        is_enrollee = tax_unit.members("is_aca_ptc_eligible", period)
        return tax_unit.max(where(is_enrollee, person_reduction, 0))
