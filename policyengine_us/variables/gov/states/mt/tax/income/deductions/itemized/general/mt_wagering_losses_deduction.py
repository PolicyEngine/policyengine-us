from policyengine_us.model_api import *


class mt_wagering_losses_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana wagering losses deduction"
    unit = USD
    documentation = (
        "The person's part of the federal wagering losses deduction, which "
        "Montana allows as an itemized deduction. Each spouse takes their "
        "own losses against their own winnings; losses beyond that go to "
        "the spouse with winnings left to absorb them, since the spouse who "
        "reports the winnings claims the losses."
    )
    definition_period = YEAR
    reference = (
        # 2023 Form 2 instructions: allocating deductions between spouses,
        # and gambling losses
        # PDF pages 13, 39
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=13",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=13",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        deduction = person.tax_unit("wagering_losses_deduction", period)
        p = parameters(period).gov.irs.deductions.itemized.wagering_losses
        # The federal deduction counts the head's and spouse's gambling.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        winnings = head_or_spouse * person("gambling_winnings", period)
        losses = head_or_spouse * person("gambling_losses", period)
        # Losses the person can deduct against their own winnings.
        own = min_(p.rate * losses, winnings)
        # What is left of the return's deduction falls on winnings that the
        # winner's own losses did not cover.
        remaining = max_(deduction - person.tax_unit.sum(own), 0)
        unused_winnings = winnings - own
        total_unused = person.tax_unit.sum(unused_winnings)
        share = np.zeros_like(total_unused)
        mask = total_unused > 0
        share[mask] = unused_winnings[mask] / total_unused[mask]
        return own + remaining * share
