from policyengine_us.model_api import *


class id_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho capital gain deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/regulation/idaho-administrative-code/title-idapa-35-tax-commission-state/rule-350101-income-tax-administrative-rules/section-350101170-idaho-capital-gains-deduction-in-general"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.capital_gains
        # taxpayer must report capital gain net income
        net_capital_gain = add(tax_unit, period, ["capital_gains"])

        # capital_gain_net_income
        net_capital_loss = tax_unit.members("capital_losses", period)
        # Idaho capital gains deduction may not be netted against
        # gains from property qualifying for the Idaho capital gains
        # deduction before the amount of the deduction is determined
        capital_gain_net_income = max_(net_capital_gain - net_capital_loss, 0)

        # Filers can deduct 60% of captial gains
        decuctions = p.percentage * net_capital_gain

        # capital gains deduction may not exceed the capital gain net income included in taxable income
        # qualified_deductions = min_(capital_gain_net_income, decuctions)

        # Ordinary Income do not qualify for the Idaho capital gains deduction
        # Gain from dispositions of certain depreciable property treated as ordinary income

        # Return calculated amount.
        return min_(capital_gain_net_income, decuctions)
