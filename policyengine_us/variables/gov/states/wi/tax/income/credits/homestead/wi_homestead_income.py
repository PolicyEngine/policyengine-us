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
        # Wis. Stat. 71.52(4)-(6): household, household income and income
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/52",
        # PDF pages 8, 13: the household is the claimant and spouse; leave
        # out children's social security and SSI.
        "https://www.revenue.wi.gov/TaxForms2024/2024-ScheduleH-inst.pdf#page=8",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        # A household is the claimant and the claimant's spouse (Wis. Stat.
        # 71.52(4)), so household income leaves out a tax unit dependent's
        # income, such as a child's social security, SSI or unemployment
        # compensation.
        income = tax_unit_non_dep_add(tax_unit, period, p.homestead.income.sources)
        disqualified_losses = tax_unit("wi_homestead_disqualified_losses", period)
        dependents = tax_unit("tax_unit_dependents", period)
        return income + disqualified_losses - dependents * p.homestead.income.exemption
