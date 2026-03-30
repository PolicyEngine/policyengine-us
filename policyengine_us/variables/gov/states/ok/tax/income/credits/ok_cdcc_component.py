from policyengine_us.model_api import *


class ok_cdcc_component(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma Child Care Credit component"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=11",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        # The OK child care/child tax credit is max(CDCC_component, CTC_component).
        # This variable extracts the CDCC portion for cross-state aggregation.
        p = parameters(period).gov.states.ok.tax.income.credits.child
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi <= p.agi_limit
        us_cdcc = tax_unit("cdcc_potential", period)
        ok_cdcc = us_cdcc * p.cdcc_fraction
        us_ctc = tax_unit("ctc_value", period)
        ok_ctc = us_ctc * p.ctc_fraction
        cdcc_is_greater = ok_cdcc >= ok_ctc
        ok_agi = tax_unit("ok_agi", period)
        agi_ratio = np.zeros_like(us_agi)
        mask = us_agi != 0
        agi_ratio[mask] = ok_agi[mask] / us_agi[mask]
        prorate = min_(1, max_(0, agi_ratio))
        return agi_eligible * prorate * cdcc_is_greater * ok_cdcc
