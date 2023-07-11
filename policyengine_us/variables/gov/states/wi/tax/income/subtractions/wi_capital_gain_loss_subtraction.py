from policyengine_us.model_api import *


class wi_capital_gain_loss_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin capital gain/loss subtraction from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleWDf.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleWDf.pdf#page=2"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # calculate Schedule WD, Line 8
        stcg_net = add(tax_unit, period, ["short_term_capital_gains"])
        # calculate Schedule WD, Line 17
        ltcg_net = add(tax_unit, period, ["long_term_capital_gains"])
        # calculate Schedule WD, Line 18
        totcg = max_(0, stcg_net + ltcg_net)
        # calculate Schedule WD, Line 20, the capital gain reduction
        p = parameters(period).gov.states.wi.tax.income.subtractions
        fraction = p.capital_gain.fraction
        cg_reduction = min_(totcg, max_(0, ltcg_net)) * fraction
        # calculate Schedule WD, Line 27, the WI reduced capital gain
        wi_cg = totcg - cg_reduction
        # calculate Schedule WD, Line 29a
        us_cg = totcg
        # return Schedule SB capital gain subtraction (WB Line 29d)
        return max_(0, us_cg - wi_cg)
