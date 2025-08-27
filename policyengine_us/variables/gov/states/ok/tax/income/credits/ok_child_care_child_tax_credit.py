from policyengine_us.model_api import *


class ok_child_care_child_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma Child Care/Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.credits
        # determine AGI eligibility
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi <= p.child.agi_limit
        # determine OK cdcc amount
        # Oklahoma matches the potential federal credit
        us_cdcc = tax_unit("cdcc_potential", period)
        ok_cdcc = us_cdcc * p.child.cdcc_fraction
        # determine OK ctc amount
        us_ctc = tax_unit("ctc", period)
        ok_ctc = us_ctc * p.child.ctc_fraction
        # determine prorated fraction
        ok_agi = tax_unit("ok_agi", period)
        # Compute OK AGI as a share of US AGI.
        # Use a mask rather than where to avoid a divide-by-zero warning.
        agi_ratio = np.zeros_like(us_agi)
        mask = us_agi != 0
        agi_ratio[mask] = ok_agi[mask] / us_agi[mask]
        prorate = min_(1, max_(0, agi_ratio))
        # receive greater of OK cdcc or OK ctc amounts prorated if AGI eligible
        return agi_eligible * prorate * max_(ok_cdcc, ok_ctc)
