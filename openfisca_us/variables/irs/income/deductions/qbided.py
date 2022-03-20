from openfisca_us.model_api import *


class qbided(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "QBI deduction"
    documentation = "Qualified Business Income (QBI) deduction"
    reference = "https://www.law.cornell.edu/uscode/text/26/199A"
    unit = USD

    def formula(tax_unit, period, parameters):
        mars = tax_unit("mars", period)
        QBINC_ELEMENTS = [
            "filer_e00900",
            "filer_e26270",
            "filer_e02100",
            "filer_e27200",
        ]
        qbinc = max_(0, add(tax_unit, period, QBINC_ELEMENTS))
        qbid = parameters(period).irs.deductions.qualified_business_interest
        lower_threshold = qbid.threshold.lower[mars]
        upper_threshold = lower_threshold + qbid.threshold.gap[mars]
        pre_qbid_taxinc = tax_unit("pre_qbid_taxinc", period)
        under_lower_threshold = pre_qbid_taxinc < lower_threshold
        between_thresholds = ~under_lower_threshold & (
            pre_qbid_taxinc < upper_threshold
        )
        above_upper_threshold = ~under_lower_threshold & ~between_thresholds
        income_is_qualified = tax_unit("pt_sstb_income", period)

        # Wage/capital limitations
        w2_wages = tax_unit("pt_binc_w2_wages", period)
        business_property = tax_unit("pt_ubia_property", period)
        wage_cap = w2_wages * qbid.cap.w2_wages.rate
        alt_cap = (
            w2_wages * qbid.cap.w2_wages.alt_rate
            + business_property * qbid.cap.business_property.rate
        )
        fraction_of_gap_passed = (
            pre_qbid_taxinc - lower_threshold
        ) / qbid.threshold.gap[mars]
        fraction_of_gap_unused = (
            upper_threshold - pre_qbid_taxinc
        ) / qbid.threshold.gap[mars]

        # Adjustments for qualified income under the upper threshold
        qbi_between_threshold_multiplier = where(
            income_is_qualified & between_thresholds,
            fraction_of_gap_unused,
            1.0,
        )
        max_qbid = (
            qbinc * qbid.pass_through_rate * qbi_between_threshold_multiplier
        )
        full_cap = max_(wage_cap, alt_cap) * qbi_between_threshold_multiplier

        # Adjustment for QBID where income is between the main thresholds
        adjustment = fraction_of_gap_passed * (max_qbid - full_cap)

        qbid_amount = select(
            (
                under_lower_threshold,
                between_thresholds,
                above_upper_threshold,
            ),
            (
                max_qbid,
                max_qbid - adjustment,
                where(income_is_qualified, 0, min_(max_qbid, full_cap)),
            ),
        )

        # Apply taxable income cap
        net_cg = add(tax_unit, period, ["filer_e00650", "c01000"])
        taxinc_cap = qbid.pass_through_rate * max_(0, pre_qbid_taxinc - net_cg)
        return min_(qbid_amount, taxinc_cap)
