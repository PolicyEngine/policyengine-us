from policyengine_us.model_api import *


class wi_homestead_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleH.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleH.pdf",
        "https://www.revenue.wi.gov/TaxForms2023/2023-ScheduleH.pdf#page=4",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        income = add(tax_unit, period, p.homestead.income.sources)
        disqualified_losses = tax_unit("wi_homestead_disqualified_losses", period)
        dependents = tax_unit("tax_unit_dependents", period)
        return (
            income + disqualified_losses - dependents * p.homestead.income.exemption
        )
