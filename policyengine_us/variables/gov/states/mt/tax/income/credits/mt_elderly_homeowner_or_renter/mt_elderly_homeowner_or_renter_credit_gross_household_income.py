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
        # 2023 Form 2 instructions, PDF pages 51-52: each household member's
        # return (line 1), nonfilers' wages (line 8), no losses (line 9).
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=51",
        # 2024 Schedule 2EC, line 17: income received by other members of
        # the household
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=48",
        # The statutory federal-AGI definition remains after the 2024 form
        # began displaying separate income categories: HB191 § 1(9), p.2.
        "https://archive.legmt.gov/bills/2021/HB0199/HB0191_X.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        sources = add(person, period, p.gross_income_sources)
        # Gross household income counts every member's federal AGI without
        # losses (§ 15-30-2337(4), (9)(a)). The dependent's gross income is
        # omitted from this return's AGI, but their own valid non-loss
        # adjustments still belong on their own return (2023 instructions,
        # line 1). Do not subtract the parent's TaxUnit-level deductions.
        ald = parameters(period).gov.irs.ald
        deduction_variables = [
            PERSON_ABOVE_THE_LINE_DEDUCTIONS[name]
            for name in ald.deductions
            if name in PERSON_ABOVE_THE_LINE_DEDUCTIONS
            and name not in ald.filer_amounts_recorded_on_dependents
        ]
        # The shared mapping uses capped/eligible person-level deductions,
        # including the dependent's own IRA deduction. It excludes loss_ald:
        # business/capital losses never reduce Montana household income.
        # Parent-owned adoption/bond exclusions recorded on dependents
        # remain with the filer under the existing convention.
        own_deductions = add(person, period, deduction_variables)
        is_dependent = person("is_tax_unit_dependent", period)
        dependent_income = is_dependent * (
            person("dependent_gross_income", period) - own_deductions
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
