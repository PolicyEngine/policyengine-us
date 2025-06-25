from policyengine_us.model_api import *


class qbi_deduction_component(Variable):
    value_type = float
    entity = Person  # NOTE: currently 1-1 person to business assumed
    label = "Qualified business income (QBI) component of the Section 199A deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1 "
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf "
        "Corresponds to Form 8995-A, Part III or Part IV."
    )

    def formula(person, period, parameters):
        # --------------------------------------------------------------
        # Section 199A Qualified Business Income (QBI) Component
        # This calculates the deduction for a single trade or business
        # before the final overall limitations are applied.
        # --------------------------------------------------------------
        p = parameters(period).gov.irs.deductions.qbi

        # --- Core Inputs ----------------------------------------------
        # QBI, W-2 wages, and UBIA for the business
        qbi = person("qualified_business_income", period)
        w2_wages = person("w2_wages_from_qualified_business", period)
        ubia_property = person("unadjusted_basis_qualified_property", period)
        is_sstb = person("business_is_sstb", period)

        # --- Taxpayer-level Inputs for Thresholds ---------------------
        # Taxable income before the QBI deduction
        taxable_income = person.tax_unit("taxable_income_less_qbid", period)
        filing_status = person.tax_unit("filing_status", period)

        # Section 199A(e)(2) - Threshold and phase-in range
        threshold = p.phase_out.start[filing_status]
        phase_in_range = p.phase_out.length[filing_status]

        # --------------------------------------------------------------
        # 1. Tentative Deduction: 20% of QBI (Section 199A(a)(1))
        # --------------------------------------------------------------
        qbi_deduction_tentative = p.max.rate * qbi  # 20% * QBI

        # --------------------------------------------------------------
        # 2. W-2 Wage and UBIA Limitation (Section 199A(b)(2))
        # --------------------------------------------------------------
        wage_limit = p.max.w2_wages.rate * w2_wages  # 50% of W-2 wages
        ubi_alt_limit = (
            p.max.w2_wages.alt_rate * w2_wages  # 25% of W-2 wages
            + p.max.business_property.rate * ubia_property  # 2.5% of UBIA
        )
        wage_ubia_limitation = max_(wage_limit, ubi_alt_limit)

        # --------------------------------------------------------------
        # 3. Phase-in Calculation (Section 199A(b)(3)(B))
        # --------------------------------------------------------------
        # The percentage of the phase-in range that has been used.
        over_threshold = max_(0, taxable_income - threshold)
        phase_in_percent = min_(1, over_threshold / phase_in_range)

        # If below threshold, this is 0. If above, this is 1.
        if phase_in_percent == 0:
            # Below threshold: Wage/UBIA limitation does not apply.
            return qbi_deduction_tentative

        # --------------------------------------------------------------
        # 4. SSTB Applicable Percentage Reduction
        # --------------------------------------------------------------
        # For SSTBs in the phase-in range, QBI, wages, and UBIA are reduced.
        # The applicable percentage is (1 - phase_in_percent).
        # For non-SSTBs, the applicable percentage is 100%.
        applicable_percent = where(is_sstb, 1 - phase_in_percent, 1)

        # Apply the SSTB reduction to the tentative deduction and the limit.
        qbi_deduction_adj = qbi_deduction_tentative * applicable_percent
        limitation_adj = wage_ubia_limitation * applicable_percent

        # The deduction is now limited by the adjusted wage/UBIA cap.
        deduction_after_limit = min_(qbi_deduction_adj, limitation_adj)

        # For an SSTB, the calculation stops here. If fully phased in (phase_in_percent=1),
        # applicable_percent is 0, so the deduction is 0.
        # For a non-SSTB, we must apply the phase-in reduction.
        if is_sstb:
            return deduction_after_limit

        # --------------------------------------------------------------
        # 5. Non-SSTB Phase-in Logic
        # --------------------------------------------------------------
        # If fully phased-in, the full limitation applies.
        if phase_in_percent == 1:
            return deduction_after_limit

        # In the phase-in range, the deduction is reduced based on how
        # far into the range the taxpayer's income is. This blends between
        # the full 20% QBI and the wage-limited amount.

        # Amount by which the 20% QBI exceeds the wage/UBIA limit.
        excess_amount = max_(0, qbi_deduction_adj - limitation_adj)

        # Reduce the tentative deduction by a phased-in portion of the excess.
        phased_in_deduction = qbi_deduction_adj - (
            excess_amount * phase_in_percent
        )

        return phased_in_deduction
