from policyengine_us.model_api import *


class qualified_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified business income deduction for tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
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
        rate = parameters(period).gov.irs.deductions.qbi.max.rate
        taxinc_cap = rate * max_(0, taxinc_less_qbid - netcg_qdiv)
        return min_(uncapped_qbid, taxinc_cap)
