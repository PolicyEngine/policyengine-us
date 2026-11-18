from policyengine_us.model_api import *
from policyengine_us.tools.mt_separate_return import mt_capital_gains_tax


class mt_capital_gains_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Montana net long-term capital gains tax when married couples file separately"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=6"  # Net Long-Term Capital Gains Tax Table
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        # The tax on capital gains comes into effect in 2024.
        if not parameters(period).gov.states.mt.tax.income.main.capital_gains.in_effect:
            return 0
        applicable_threshold = person(
            "mt_capital_gains_tax_applicable_threshold_indiv", period
        )
        return mt_capital_gains_tax(person, period, parameters, applicable_threshold)
