from policyengine_us.model_api import *


class qualified_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified business income deduction for tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1",
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf",
    )

    def formula(tax_unit, period, parameters):
        # compute sum of QBID amounts for each person in TaxUnit following
        # logic in 2018 IRS Publication 535, Worksheet 12-A, line 16
        person = tax_unit.members
        qbid_amt = person("qbid_amount", period)
        uncapped_qbid = tax_unit.sum(qbid_amt)
        # apply taxinc cap at the TaxUnit level following logic
        # in 2018 IRS Publication 535, Worksheet 12-A, lines 32-37
        taxinc_less_qbid = tax_unit("taxable_income_less_qbid", period)
        netcg_qdiv = tax_unit("adjusted_net_capital_gain", period)
        p = parameters(period).gov.irs.deductions.qbi
        taxinc_cap = p.max.rate * max_(0, taxinc_less_qbid - netcg_qdiv)
        pre_floor_qbid = min_(uncapped_qbid, taxinc_cap)
        if p.deduction_floor.in_effect:
            # Section 199A(i) uses eligible QBI: apply the section 199A(d)(3)
            # SSTB exclusion before netting signed income for the minimum.
            filing_status = tax_unit("filing_status", period)
            excess = max_(0, taxinc_less_qbid - p.phase_out.start[filing_status])
            length = p.phase_out.length[filing_status]
            reduction = np.divide(
                excess, length, out=np.ones_like(excess, dtype=float), where=length > 0
            )
            applicable_rate = 1 - min_(1, reduction)
            qbi = person("qualified_business_income", period)
            legacy_sstb = person("business_is_sstb", period)
            non_sstb = where(legacy_sstb, 0, qbi)
            sstb = person("sstb_qualified_business_income", period) + where(
                legacy_sstb, qbi, 0
            )
            total_qbi = tax_unit.sum(
                non_sstb + sstb * tax_unit.project(applicable_rate)
            )
            floor = p.deduction_floor.amount.calc(total_qbi)
            return max_(pre_floor_qbid, floor)
        return pre_floor_qbid
