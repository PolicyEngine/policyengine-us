from policyengine_us.model_api import *


class mt_federal_income_tax_deduction_indiv(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana federal income tax deduction when married couples are filing separately"
    reference = (
        "https://law.justia.com/codes/montana/2021/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2021) (1)(b)
        # 2022 Form 2 instructions, Itemized Deductions Schedule, line 4
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=33",
    )
    unit = USD
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.itemized.federal_income_tax
        if not p.applies:
            return 0
        # Federal income tax is reported by the spouse who earned the income
        # it was paid on, and each spouse is held to their own cap; the
        # deduction cannot be arbitrarily allocated. Without each spouse's
        # federal withholding, attribute the couple's federal income tax by
        # each spouse's share of federal adjusted gross income, then cap it.
        federal_income_tax = max_(
            person.tax_unit("income_tax_before_refundable_credits", period), 0
        )
        share = person("mt_federal_income_tax_deduction_share", period)
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        return min_(federal_income_tax * share, p.cap[filing_status])
