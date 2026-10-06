from policyengine_us.model_api import *


class mt_federal_income_tax_deduction_share(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Share of the couple's federal income tax attributed to each spouse for the Montana deduction"
    reference = (
        # 2022 Form 2 instructions, Itemized Deductions Schedule, line 4a:
        # "If you are married filing separately with your spouse, the federal
        # income tax withheld should be reported by the spouse who earned the
        # income."
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=33",
    )
    unit = "/1"
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        # Each filer's share of the federal income the tax was paid on,
        # counting only positive federal adjusted gross income. A dependent's
        # income is on the dependent's own return. With no positive income,
        # the tax is attributed to the head.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        income = head_or_spouse * max_(
            person("adjusted_gross_income_person", period), 0
        )
        total_income = person.tax_unit.sum(income)
        share = np.zeros_like(total_income)
        mask = total_income > 0
        share[mask] = income[mask] / total_income[mask]
        head = person("is_tax_unit_head", period)
        return where(total_income > 0, share, head)
