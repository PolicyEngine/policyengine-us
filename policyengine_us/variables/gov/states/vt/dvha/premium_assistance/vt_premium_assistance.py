from policyengine_us.model_api import *


class vt_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "vt_premium_assistance_eligible"
    reference = (
        "https://legislature.vermont.gov/statutes/section/33/018/01812",
        "https://info.healthconnect.vermont.gov/financial-help",
    )
    documentation = (
        "Vermont state top-up to the federal ACA premium tax credit, an "
        "incremental subsidy the State pays directly to the insurer on top of "
        "the federal advance premium tax credit. Vermont applies a flat 1.5 "
        "percentage-point reduction to the federal section 36B applicable "
        "percentage, so the subsidy equals the enrollee's income times that "
        "reduction, capped at the benchmark premium remaining after the federal "
        "APTC so it never duplicates the federal credit. The benchmark second-"
        "lowest-cost silver plan premium (slcsp) is annualized from its monthly "
        "definition. At very low income the applicable percentage can fall below "
        "1.5%, in which case the reduction floors at zero and the cap lets "
        "Vermont Premium Assistance cover the full residual premium after the "
        "federal APTC. The amount is not taxable. Advance-payment, "
        "reconciliation, and insurer-payment mechanics, and the separate "
        "cost-sharing reduction program under 33 V.S.A. section 1812(b), are "
        "not modeled."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.dvha.premium_assistance
        # Clamp income to zero so a negative ACA MAGI cannot inflate the gap.
        income = max_(tax_unit("aca_magi", period), 0)
        federal_percentage = tax_unit("aca_required_contribution_percentage", period)
        # Statute 33 V.S.A. § 1812(a)(2) says "reduce the premium contribution
        # ... by 1.5 percent" and defers the applicable-percentage table to
        # federal section 36B; DVHA operationalizes this as a 1.5
        # PERCENTAGE-POINT cut to that section 36B applicable percentage, not a
        # proportional scaling. That is why 0.015 is SUBTRACTED from
        # aca_required_contribution_percentage rather than multiplied — this is
        # intentional, not a units bug.
        reduction = p.applicable_percentage_reduction
        # The reduction floors at zero: if the federal applicable percentage is
        # already below 1.5%, the Vermont percentage bottoms out at 0 so the
        # gap factor below becomes the FULL federal percentage (VPA then covers
        # the entire enrollee contribution). This branch is organically
        # unreachable in the 2026 baseline because the federal applicable
        # percentage floors at 2.10% > 1.5%, but is retained for robustness and
        # future contribution schedules.
        vt_percentage = max_(0, federal_percentage - reduction)
        # Incremental contribution gap between the federal applicable
        # percentage and the lower Vermont percentage.
        contribution_gap = max_(0, income * (federal_percentage - vt_percentage))
        # slcsp is a MONTH-period variable; annualize it to match aca_ptc.
        slcsp = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        # Cap at the premium balance remaining after the federal APTC.
        premium_after_aptc = max_(0, slcsp - aca_ptc)
        return min_(contribution_gap, premium_after_aptc)
