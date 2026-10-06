from policyengine_us.model_api import *


class mt_casualty_loss_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Montana casualty and theft loss deduction when married couples file separately"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # 2022 Form 2 instructions, Itemized Deductions Schedule, line 15
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=35",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=36",
        # 2022 Form 2 instructions, allocation of deductions when filing separately
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=11",
    )
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if not p.casualty_loss.applies:
            return 0
        # Spouses filing separately each complete a separate federal Form 4684
        # for their own loss, using their own Montana adjusted gross income in
        # place of federal adjusted gross income. A deduction attributable to
        # only one spouse must be claimed by that spouse.
        p_casualty = parameters(period).gov.irs.deductions.itemized.casualty
        own_loss = person("casualty_loss", period)
        # Dependents' losses go to the head, as mt_agi_indiv does with
        # dependents' income.
        is_dependent = person("is_tax_unit_dependent", period)
        is_head = person("is_tax_unit_head", period)
        dependents_loss = person.tax_unit.sum(is_dependent * own_loss)
        loss = ~is_dependent * own_loss + is_head * dependents_loss
        agi = person("mt_agi_indiv", period)
        return p_casualty.active * max_(loss - agi * p_casualty.floor, 0)
