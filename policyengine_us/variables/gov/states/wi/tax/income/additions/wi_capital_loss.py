from policyengine_us.model_api import *


class wi_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin capital loss (limited differently than US capital loss)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleWDf.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleWDf.pdf#page=2"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # calculate Schedule WD, Line 18
        GAIN_SOURCES = ["short_term_capital_gains", "long_term_capital_gains"]
        netcg = add(tax_unit, period, GAIN_SOURCES)
        # return Schedule WD, Line 28, as a positive amount as on form
        p = parameters(period).gov.states.wi.tax.income.additions
        limit = p.capital_loss.limit
        return where(netcg < 0, min_(limit, -netcg), 0)
