from policyengine_us.model_api import *


class mt_wagering_losses_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana wagering losses deduction"
    unit = USD
    documentation = (
        "The person's part of the federal wagering losses deduction, which "
        "Montana allows as an itemized deduction. When spouses file "
        "separately, the spouse who reports the gambling winnings claims "
        "the losses."
    )
    definition_period = YEAR
    reference = (
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=39",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=13",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        deduction = person.tax_unit("wagering_losses_deduction", period)
        # The federal deduction counts the head's and spouse's gambling.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        winnings = head_or_spouse * person("gambling_winnings", period)
        total_winnings = person.tax_unit.sum(winnings)
        share = np.zeros_like(total_winnings)
        mask = total_winnings > 0
        share[mask] = winnings[mask] / total_winnings[mask]
        return deduction * share
