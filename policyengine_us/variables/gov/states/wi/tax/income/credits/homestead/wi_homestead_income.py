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
        # Wis. Stat. 71.52(4)-(6): household, income and qualifying repayments.
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/52",
        # PDF pages 8, 12-13: claimant/spouse household, qualifying repayments,
        # and exclusion of children's social security and SSI.
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
        # The filer Social Security source floors combined net benefits at
        # zero for federal taxability. Wisconsin allows qualifying repayments
        # of prior-year nontaxable household income (71.52(6); 2024 Schedule H
        # instructions, page 12). Treat negative net benefits as qualifying
        # repayments; prior inclusion cannot be checked without claim history.
        # Combine spouses first, so repayments already offset by a spouse's
        # positive benefits are not subtracted twice. Leave dependents out.
        net_social_security = tax_unit_non_dep_add(
            tax_unit, period, ["social_security"]
        )
        income += min_(net_social_security, 0)
        disqualified_losses = tax_unit("wi_homestead_disqualified_losses", period)
        dependents = tax_unit("tax_unit_dependents", period)
        return income + disqualified_losses - dependents * p.homestead.income.exemption
