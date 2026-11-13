from policyengine_us.model_api import *
from policyengine_us.tools.mt_separate_return import mt_capital_gains_threshold


class mt_capital_gains_tax_applicable_threshold_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana applicable threshold for the capital gains tax when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=6"  # Net Long-Term Capital Gains Tax Table
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        taxable_income = person("mt_taxable_income_indiv", period)
        return mt_capital_gains_threshold(person, period, parameters, taxable_income)
