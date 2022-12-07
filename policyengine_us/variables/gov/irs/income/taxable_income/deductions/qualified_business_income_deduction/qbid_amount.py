from policyengine_us.model_api import *


class qbid_amount(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income deduction amount for a person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions
        # compute maximum QBID amount
        qbi = person("qualified_business_income", period)
        qbid_max = p.qbi.max.rate * qbi
        # compute full cap on maximum QBID amount following
        # logic in 2018 Publication 535, Worksheet 12-A
        w2_wages = person("w2_wages_from_qualified_business", period)
        b_property = person("unadjusted_basis_qualified_property", period)
        wage_cap = w2_wages * p.qbi.max.w2_wages.rate
        alt_cap = (
            w2_wages * p.qbi.max.w2_wages.alt_rate
            + b_property * p.qbi.max.business_property.rate
        )
        full_cap = max_(wage_cap, alt_cap)
        # compute phase-out thresholds per Worksheet 12-A, Part III
        taxinc_less_qbid = person.tax_unit("taxable_income_less_qbid", period)
        filing_status = person.tax_unit("filing_status", period)
        po_start = p.qbi.phase_out.start[filing_status]
        po_length = p.qbi.phase_out.length[filing_status]
        po_end = po_start + po_length
        # compute phase-out limited QBID amount following
        # logic in 2018 Publication 535, Sch A and Worksheet 12-A
        pfrac = min_(1, (max_(0, taxinc_less_qbid - po_start)) / po_length)
        afrac = 1 - pfrac  # Sch A, line 10
        is_sstb = person("business_is_sstb", period)
        adj_qbid_max = where(
            is_sstb,
            qbid_max * afrac,  # Sch A, line 11
            qbid_max  # Worksheet 12-A, line 3
        )
        adj_cap = where(
            is_sstb,
            full_cap * afrac,  # Sch A, line 12 and line 13
            full_cap  # Worksheet 12-A, line 10
        )
        line11 = min_(qbid_max, adj_cap)  # Worksheet 12-A, line 11
        # compute phased reduction following logic in Worksheet 12-A
        reduction = pfrac * max_(0, qbid_max - adj_cap)  # line 25
        line26 = max_(0, qbid_max - reduction)
        line12 = where(full_cap < qbid_max, line26, 0)
        qbid_limited = max_(line11, line12)  # line 13
        # compute QBID amount
        return where(
            taxinc_less_qbid <= po_start,
            qbid_max,
            where(
                np.logical_and(is_sstb, taxinc_less_qbid >= po_end),
                0,
                where(
                    np.logical_and(~is_sstb, taxinc_less_qbid >= po_end),
                    min_(qbid_max, full_cap),
                    qbid_limited
                )
            )
        )

