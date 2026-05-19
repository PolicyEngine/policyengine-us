from policyengine_us.model_api import *


class qbid_amount(Variable):
    value_type = float
    entity = Person
    label = "Per-person qualified business income deduction amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1",
        "https://www.law.cornell.edu/uscode/text/26/199A#d_3",
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf",
        "https://www.irs.gov/pub/irs-pdf/f8995.pdf",
        "https://www.irs.gov/pub/irs-pdf/f8995a.pdf",
    )

    def formula(person, period, parameters):
        # Computations follow logic in 2018 IRS Publication 535,
        # Worksheet 12-A (and Schedule A for SSTB). The non-SSTB and SSTB
        # categories are computed separately so the §199A(d)(3) applicable-
        # percentage phaseout reduces only the SSTB component above the
        # threshold (Form 8995-A, Part II, columns A vs. B).
        p = parameters(period).gov.irs.deductions.qbi
        # Phase-out range
        taxinc_less_qbid = person.tax_unit("taxable_income_less_qbid", period)
        filing_status = person.tax_unit("filing_status", period)
        po_start = p.phase_out.start[filing_status]
        po_length = p.phase_out.length[filing_status]
        reduction_rate = min_(  # Worksheet 12-A, line 24; Schedule A, line 9
            1, (max_(0, taxinc_less_qbid - po_start)) / po_length
        )
        applicable_rate = 1 - reduction_rate  # Schedule A, line 10
        total_w2_wages = person("w2_wages_from_qualified_business", period)
        total_b_property = person("unadjusted_basis_qualified_property", period)

        def qbi_component(qbi, full_cap, sstb_multiplier):
            # Worksheet 12-A lines 3, 11-13 / Schedule A lines 9-12.
            qbid_max = p.max.rate * qbi  # Worksheet 12-A, line 3
            adj_qbid_max = qbid_max * sstb_multiplier
            adj_cap = full_cap * sstb_multiplier
            line11 = min_(adj_qbid_max, adj_cap)
            reduction = reduction_rate * max_(0, adj_qbid_max - adj_cap)
            line26 = max_(0, adj_qbid_max - reduction)
            line12 = where(adj_cap < adj_qbid_max, line26, 0)
            return max_(line11, line12)

        # Non-SSTB and SSTB QBI categories. Backward compatibility:
        # if the legacy `business_is_sstb` flag is set, route the legacy
        # `qualified_business_income` into the SSTB component so the
        # phaseout still applies.
        non_sstb_qbi = person("qualified_business_income", period)
        sstb_qbi_from_se = person("sstb_qualified_business_income", period)
        is_sstb_legacy = person("business_is_sstb", period)
        sstb_qbi = sstb_qbi_from_se + where(is_sstb_legacy, non_sstb_qbi, 0)
        non_sstb_qbi_final = where(is_sstb_legacy, 0, non_sstb_qbi)

        has_non_sstb = non_sstb_qbi_final > 0
        has_sstb = sstb_qbi > 0
        has_mixed_categories = has_non_sstb & has_sstb

        # Schedule A applies the SSTB applicable percentage to the SSTB's own
        # allocable W-2 wages and UBIA. The model stores person-level totals,
        # so mixed cases use explicit SSTB allocable inputs to split those
        # totals without double counting the same wage/property pool twice.
        sstb_w2_wages = where(
            is_sstb_legacy,
            total_w2_wages,
            where(
                has_mixed_categories,
                person("sstb_w2_wages_from_qualified_business", period),
                where(has_sstb, total_w2_wages, 0),
            ),
        )
        non_sstb_w2_wages = where(
            is_sstb_legacy,
            0,
            where(
                has_mixed_categories,
                max_(0, total_w2_wages - sstb_w2_wages),
                where(has_non_sstb, total_w2_wages, 0),
            ),
        )

        sstb_b_property = where(
            is_sstb_legacy,
            total_b_property,
            where(
                has_mixed_categories,
                person("sstb_unadjusted_basis_qualified_property", period),
                where(has_sstb, total_b_property, 0),
            ),
        )
        non_sstb_b_property = where(
            is_sstb_legacy,
            0,
            where(
                has_mixed_categories,
                max_(0, total_b_property - sstb_b_property),
                where(has_non_sstb, total_b_property, 0),
            ),
        )

        def full_cap(w2_wages, b_property):
            wage_cap = w2_wages * p.max.w2_wages.rate  # Worksheet 12-A, line 5
            alt_cap = (  # Worksheet 12-A, line 9
                w2_wages * p.max.w2_wages.alt_rate
                + b_property * p.max.business_property.rate
            )
            return max_(wage_cap, alt_cap)  # Worksheet 12-A, line 10

        non_sstb_component = qbi_component(
            non_sstb_qbi_final,
            full_cap(non_sstb_w2_wages, non_sstb_b_property),
            1,
        )
        sstb_component = qbi_component(
            sstb_qbi,
            full_cap(sstb_w2_wages, sstb_b_property),
            applicable_rate,
        )

        # REIT/PTP component (Form 8995 Lines 6-9).
        # Per §199A(b)(1)(B), qualified REIT dividends and qualified PTP
        # income receive a 20% deduction WITHOUT W-2 wage or UBIA limitations.
        reit_ptp_income = person("qualified_reit_and_ptp_income", period)
        reit_ptp_component = p.max.reit_ptp_rate * max_(0, reit_ptp_income)

        # Total QBID = non-SSTB + SSTB + REIT/PTP (Form 8995 Line 10).
        return non_sstb_component + sstb_component + reit_ptp_component
