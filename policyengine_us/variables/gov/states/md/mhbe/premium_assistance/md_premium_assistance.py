from policyengine_us.model_api import *


class md_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "md_premium_assistance_eligible"
    reference = (
        "https://mgaleg.maryland.gov/pubs/committee/AELR/25-134E-Regulation.pdf#page=5",
        "https://mgaleg.maryland.gov/meeting_material/2025/hgo%20-%20134051066649659653%20-%20Combined%20MHBE.MIA%20slides_10.16.2025%20briefing%20to%20HGO&Finance.pdf#page=58",
    )
    documentation = (
        "Maryland state top-up to the federal ACA premium tax credit. The "
        "subsidy reduces the enrollee's required contribution toward the "
        "benchmark SLCSP from the federal applicable percentage down to the "
        "lower Maryland target percentage, capped at the premium remaining "
        "after the federal APTC so it never duplicates the federal credit. "
        "For enrollees with a 0% target contribution the program also covers "
        "the non-essential-health-benefit premium components so their net "
        "premium is $0, but this non-EHB split is not modeled here "
        "(COMAR 14.35.21.04)."
    )

    def formula(tax_unit, period, parameters):
        income = max_(tax_unit("aca_magi", period), 0)
        federal_percentage = tax_unit("aca_required_contribution_percentage", period)
        md_percentage = tax_unit(
            "md_premium_assistance_target_contribution_percentage", period
        )
        # Contribution gap between the federal applicable percentage and the
        # lower Maryland target percentage.
        contribution_gap = max_(0, income * (federal_percentage - md_percentage))
        # slcsp is a MONTH-period variable; core sums the 12 months when
        # called from this YEAR formula.
        slcsp = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        # Cap at the premium balance remaining after the federal APTC.
        premium_after_aptc = max_(0, slcsp - aca_ptc)
        return min_(contribution_gap, premium_after_aptc)
