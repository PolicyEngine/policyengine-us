from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.dependent_taxable_ss_magi import (
    PERSON_ABOVE_THE_LINE_DEDUCTIONS,
)


class mt_elderly_homeowner_or_renter_credit_gross_household_income(Variable):
    value_type = float
    entity = Person
    label = "Montana gross household income for the elderly homeowner/renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-23/section-15-30-2337/",
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # 2023 Form 2 instructions, Elderly Homeowner/Renter Credit Schedule, line 9
        # (renamed Schedule 2EC from 2024)
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=52",
        # 2023 instructions, lines 1 and 8: the returns of each member of
        # the household, and the wages of members who do not file
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=51",
        # 2024 Schedule 2EC, line 17: income received by other members of
        # the household
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=48",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        sources = add(person, period, p.gross_income_sources)
        # Gross household income counts every member of the household
        # (§ 15-30-2337(4)). A tax unit dependent's income is on their own
        # return, not in adjusted_gross_income_person (irs_gross_income
        # leaves dependents out). Start with their gross income without
        # losses, then retain the permitted non-loss AGI adjustments
        # attributable to that person (2023 instructions, lines 1 and 9).
        # Do not floor an individual's AGI contribution at zero: an
        # adjustment such as an early-withdrawal penalty can exceed income.
        is_dependent = person("is_tax_unit_dependent", period)
        deductions = [
            PERSON_ABOVE_THE_LINE_DEDUCTIONS[deduction]
            for deduction in parameters(period).gov.irs.ald.deductions
            if deduction in PERSON_ABOVE_THE_LINE_DEDUCTIONS
        ]
        dependent_income = is_dependent * (
            person("dependent_gross_income", period) - add(person, period, deductions)
        )
        # The income above counts only the taxable portion of Social
        # Security: a filer's in federal AGI, a dependent's in their own
        # gross income. Add the untaxed portion so all SS is counted per
        # § 15-30-2337(9)(a)(viii).
        social_security = person("social_security", period)
        taxable_social_security = add(
            person,
            period,
            ["taxable_social_security", "dependent_taxable_social_security"],
        )
        untaxed_social_security = max_(social_security - taxable_social_security, 0)
        # Income is federal AGI "without regard to loss" (§ 15-30-2337(9)(a)),
        # so the business and capital losses deducted in computing federal
        # AGI are added back (2023 Elderly Homeowner/Renter Credit Schedule,
        # line 9: "The gross household income cannot be reduced by any
        # losses."). The return's losses are added once, to the head.
        head = person("is_tax_unit_head", period)
        losses = head * person.tax_unit("loss_ald", period)
        return sources + dependent_income + untaxed_social_security + losses
