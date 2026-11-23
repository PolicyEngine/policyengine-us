from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_alimony_addback(Variable):
    value_type = float
    entity = Person
    label = "Montana elderly homeowner/renter credit alimony add-back"
    documentation = (
        "Alimony a household member received that neither federal adjusted "
        "gross income nor a dependent's own gross income counts. For a filer "
        "this is alimony under a divorce or separation instrument executed "
        "after 2018, which federal gross income leaves out; gross household "
        "income counts all alimony received as nontaxable income. For a "
        "person recorded as both a dependent and the head or spouse, whom "
        "neither income path counts, it is all of their alimony."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # § 15-30-2337(9)(a)(iii): federal adjusted gross income "plus all
        # nontaxable income, including but not limited to ... alimony"
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # 2025 Schedule 2EC, line 9: "Enter the total of all alimony received
        # during the year"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=46",
        # Alimony under an instrument executed after 2018 is not in the
        # recipient's federal gross income (Pub. L. 115-97 § 11051)
        "https://www.irs.gov/taxtopics/tc452",
    )

    def formula(person, period, parameters):
        # Federal AGI already counts a filer's taxable alimony
        # (irs_gross_income counts people who are not dependents), and a
        # dependent's own gross income counts a dependent's
        # (dependent_gross_income counts people who are not the head or
        # spouse). Add the rest of the alimony received.
        received = max_(0, person("alimony_income", period))
        is_dependent = person("is_tax_unit_dependent", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        taxable = max_(0, person("taxable_alimony_income", period))
        counted = where(is_dependent, ~head_or_spouse * taxable, taxable)
        return max_(received - counted, 0)
