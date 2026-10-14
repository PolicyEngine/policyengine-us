from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_unemployment_compensation_addback(Variable):
    value_type = float
    entity = Person
    label = "Montana elderly homeowner/renter credit unemployment compensation add-back"
    documentation = (
        "Unemployment compensation a household member received that neither "
        "federal adjusted gross income nor a dependent's own gross income "
        "counts. For a filer this is the part excluded from 2020 federal "
        "gross income under IRC 85(c), which gross household income counts as "
        "nontaxable income. For a person recorded as both a dependent and the "
        "head or spouse, whom neither income path counts, it is all of their "
        "compensation."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # § 15-30-2337(9)(a): federal adjusted gross income "plus all
        # nontaxable income"
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # IRC 85(c), added by ARPA § 9042: up to $10,200 of 2020
        # unemployment compensation excluded from gross income
        "https://www.law.cornell.edu/uscode/text/26/85#c",
        # 2020 Form 2 instructions, line 8: "Enter all items of income
        # received by the members of the household that were not reported on
        # lines 1 through 7"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2020_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=45",
        # 2024 Schedule 2EC, line 14: "Enter the total of unemployment
        # compensation received during the year"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=48",
    )

    def formula(person, period, parameters):
        # Gross household income counts all the unemployment compensation a
        # member received, taxable or not. Federal AGI already counts the
        # taxable part of a filer's (irs_gross_income counts people who are
        # not dependents), and a dependent's own gross income counts all of a
        # dependent's (dependent_gross_income counts people who are not the
        # head or spouse, without the IRC 85(c) exclusion). Add the rest.
        received = max_(0, person("total_unemployment_compensation", period))
        is_dependent = person("is_tax_unit_dependent", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        taxable = max_(0, person("taxable_unemployment_compensation", period))
        counted = where(is_dependent, ~head_or_spouse * received, taxable)
        return max_(received - counted, 0)
