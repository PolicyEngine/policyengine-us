from policyengine_us.model_api import *


class alternative_tax_on_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii alternative tax on capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.hi.tax.income.computation
        taxable_income = tax_unit("taxable_income", period)
        net_lt_capital_gain = add(person, period, ["long_term_capital_gains"])
        net_capital_gain = tax_unit("net_capital_gain", period)
         # - line_9 how to calculate Net gain from the disposition of property held for investment
        claimed = p.alternative_tax_claim[filing_status]
        ineligible_income = max_(
            taxable_income - min_(net_capital_gain, net_lt_capital_gain),
            claimed
        )  #line_13 how to calculate the tax according to Tax Table or Tax Rate Schedules
        eligible_income = taxable_income - ineligible_income

        #ineligible_tax =  line 15 (tax for line 13)
        #taxable_income_tax =  line 18 (tax for taxable income)

        alternative_tax = ineligible_tax + eligible_income * p.alternative_tax_rate  #line 17
    
        return min_(taxable_income_tax, alternative_tax)