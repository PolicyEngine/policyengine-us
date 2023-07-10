from policyengine_us.model_api import *


class wi_capgain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin capital gain (which is different from US capital gain)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleWDf.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleWDf.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # calculate Schedule WD, Line 8
        stcg_pos = add(tax_unit, period, ["short_term_capital_gains"])
        stcg_neg = add(tax_unit, period, ["short_term_capital_losses"])
        stcg_net = stcg_pos - stcg_neg
        # calculate Schedule WD, Line 17
        ltcg_pos = add(tax_unit, period, ["long_term_capital_gains"])
        ltcg_neg = add(tax_unit, period, ["long_term_capital_losses"])
        ltcg_net = ltcg_pos - ltcg_neg
        # calculate Schedule WD, Line 18
        totcg = max_(0, stcg_net + ltcg_net)
        # calculate Schedule WD, Line 20, the capital gain reduction
        p = parameters(period).gov.states.wi.tax.income.subtractions
        fraction = p.capital_gain.fraction
        cg_reduction = min_(totcg, max_(0, ltcg_net)) * fraction
        # return Schedule WD, Line 27, the reduced capgain
        return totcg - cg_reduction
