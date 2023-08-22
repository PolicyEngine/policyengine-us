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
        net_capital_gain = tax_unit("net_capital_gain", period)

        # Filers can deduct 60% of captial gains

        # Ordinary Income do not qualify for the Idaho capital gains deduction
        # Gain from dispositions of certain depreciable property treated as ordinary income

        # Return calculated amount.
        return p.percentage * net_capital_gain
