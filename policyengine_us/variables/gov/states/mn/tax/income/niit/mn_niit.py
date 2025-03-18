from policyengine_us.model_api import *


class mn_niit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Net Investment Income Tax (NIIT)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2024-12/m1m-24.pdf"
        "https://www.revisor.mn.gov/statutes/cite/290.033"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        """
        Computes Minnesota's net investment income tax using a bracket structure.
        Currently, the brackets are defined such that:
          - Amounts up to $1,000,000 are taxed at 0%
          - Amounts above $1,000,000 are taxed at 1%
        """
        p = parameters(period).gov.states.mn.tax.income.niit
        # Minnesota defines its NIIT base following the IRC, except exempting
        # gains from some agricultural/rural/forested land. We do not account
        # for this exemption.
        net_investment_income = tax_unit("net_investment_income", period)
        return p.rate.calc(net_investment_income)
