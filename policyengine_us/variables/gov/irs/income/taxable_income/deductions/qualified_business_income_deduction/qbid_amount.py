from policyengine_us.model_api import *


class qbid_amount(Variable):
    value_type = float
    entity = Person
    label = (
        "Per-cap qualified business income deduction amount for each person"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
    )

    def formula(person, period, parameters):
        # computations follow logic in 2018 IRS Publication 535,
        # Worksheet 12-A (and Schedule A for SSTB)
        p = parameters(period).gov.irs.deductions.qbi
        # compute maximum QBID amount
        qbi = person("qualified_business_income", period)
        qbid_max = p.max.rate * qbi  # Worksheet 12-A, line 3
        # compute caps
        w2_wages = person("w2_wages_from_qualified_business", period)
        b_property = person("unadjusted_basis_qualified_property", period)
        wage_cap = w2_wages * p.max.w2_wages.rate  # Worksheet 12-A, line 5
        alt_cap = (  # Worksheet 12-A, line 9
            w2_wages * p.max.w2_wages.alt_rate
            + b_property * p.max.business_property.rate
        )
        full_cap = max_(wage_cap, alt_cap)  # Worksheet 12-A, line 10
        # compute phase-out ranges
        taxinc_less_qbid = person.tax_unit("taxable_income_less_qbid", period)
        filing_status = person.tax_unit("filing_status", period)
        po_start = p.phase_out.start[filing_status]
        po_length = p.phase_out.length[filing_status]
        # compute phase-out limited QBID amount
        reduction_rate = min_(  # Worksheet 12-A, line 24; Schedule A, line 9
            1, (max_(0, taxinc_less_qbid - po_start)) / po_length
        )
        applicable_rate = 1 - reduction_rate  # Schedule A, line 10
        is_sstb = person("business_is_sstb", period)
        # Schedule A, line 11
        sstb_multiplier = where(is_sstb, applicable_rate, 1)
        adj_qbid_max = qbid_max * sstb_multiplier
        # Schedule A, line 12 and line 13
        adj_cap = full_cap * sstb_multiplier
        line11 = min_(adj_qbid_max, adj_cap)  # Worksheet 12-A, line 11
        # compute phased reduction
        reduction = reduction_rate * max_(  # Worksheet 12-A, line 25
            0, adj_qbid_max - adj_cap
        )
        line26 = max_(0, adj_qbid_max - reduction)
        line12 = where(adj_cap < adj_qbid_max, line26, 0)
        return max_(line11, line12)  # Worksheet 12-A, line 13
