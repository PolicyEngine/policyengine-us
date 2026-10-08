from policyengine_us.model_api import *


class mt_state_income_tax_addition(Variable):
    value_type = float
    entity = Person
    label = "Montana state income tax addition on Schedule I line 4"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=22"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.additions
        if p.state_income_tax_reduces_federal_deduction:
            return 0
        is_head = person("is_tax_unit_head", period)
        return is_head * person.tax_unit("mt_state_income_tax_addback", period)
