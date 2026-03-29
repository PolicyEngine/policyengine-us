from policyengine_us.model_api import *


def _taxsim_ok_child_credit_components(tax_unit, period, parameters):
    p = parameters(period).gov.states.ok.tax.income.credits.child
    us_agi = tax_unit("adjusted_gross_income", period)
    agi_eligible = us_agi <= p.agi_limit

    us_cdcc = tax_unit("cdcc_potential", period)
    ok_cdcc = us_cdcc * p.cdcc_fraction

    us_ctc = tax_unit("ctc_value", period)
    ok_ctc = us_ctc * p.ctc_fraction

    ok_agi = tax_unit("ok_agi", period)
    agi_ratio = np.zeros_like(us_agi)
    mask = us_agi != 0
    agi_ratio[mask] = ok_agi[mask] / us_agi[mask]
    prorate = min_(1, max_(0, agi_ratio))

    child_care_credit = agi_eligible * prorate * ok_cdcc
    child_tax_credit = agi_eligible * prorate * ok_ctc

    return (
        where(child_care_credit >= child_tax_credit, child_care_credit, 0),
        where(child_tax_credit > child_care_credit, child_tax_credit, 0),
    )


class taxsim_ok_child_care_credit_component(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility Oklahoma child care credit component"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        return _taxsim_ok_child_credit_components(tax_unit, period, parameters)[0]


class taxsim_ok_child_tax_credit_component(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility Oklahoma child tax credit component"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        return _taxsim_ok_child_credit_components(tax_unit, period, parameters)[1]
