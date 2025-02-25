from policyengine_us.model_api import *

class mn_niit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Net Investment Income Tax (NIIT)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2024-12/m1-24.pdf"
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
        net_investment_income = tax_unit("net_investment_income", period)
        total_niit = 0.0
        previous_threshold = 0
        for i, bracket in enumerate(p):
            bracket_threshold = bracket.threshold
            bracket_rate = bracket.rate
            # if bracket_threshold is None or missing, treat it as unbounded
            if bracket_threshold is None:
                # everything above 'previous_threshold' is taxed in this bracket
                taxable_in_this_bracket = max(0, net_investment_income - previous_threshold)
            else:
                taxable_in_this_bracket = max(0,
                    min(net_investment_income, bracket_threshold) - previous_threshold)
            # tax due in this bracket
            bracket_tax = taxable_in_this_bracket * bracket_rate
            total_niit = total_niit + bracket_tax
            if bracket_threshold is None:
                break
            else:
                previous_threshold = bracket_threshold
            # if net_investment_income is below this bracket, stop
            if net_investment_income <= bracket_threshold:
                break

        return total_niit