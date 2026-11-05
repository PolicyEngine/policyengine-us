from policyengine_us.model_api import *


class mt_loss_ald_reallocation(Variable):
    value_type = float
    entity = Person
    label = "Montana reallocation of business and capital losses between spouses"
    unit = USD
    documentation = (
        "Each spouse's federal business and capital loss deduction "
        "(loss_ald_person) less an equal share of the return's loss_ald. "
        "Montana's own allocation of losses between spouses who file "
        "separately on the same form is not modeled here: the capital loss "
        "elections of ARM 42.15.206(3), and the Section 461(l) limit "
        "recomputed with the single filer's threshold. Until it is, Montana "
        "divides the return's losses equally between the spouses, as "
        "PolicyEngine did before each spouse's own deductions were "
        "attributed to them. Adding this amount to a spouse's federal AGI "
        "gives that equal division. Other deductions stay with the spouse "
        "who has them. It applies through 2023: from 2024 spouses no longer "
        "file separately on the same form, and Montana no longer allocates "
        "losses between them."
    )
    definition_period = YEAR
    defined_for = "mt_married_filing_separately_on_same_return_eligible"
    reference = (
        "https://sosmt.gov/wp-content/uploads/attachments/MAR10-05.pdf#page=35",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=23",
        # 2024 Form 2 instructions, page i: "Capital losses, passive losses,
        # and excess business losses will no longer be allocated by spouse".
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=5",
    )

    def formula(person, period, parameters):
        loss_ald = person.tax_unit("loss_ald", period)
        equal_share = filer_share(person, period, 0 * loss_ald)
        return person("loss_ald_person", period) - loss_ald * equal_share
