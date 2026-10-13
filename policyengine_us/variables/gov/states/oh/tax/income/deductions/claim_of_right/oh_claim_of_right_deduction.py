from policyengine_us.model_api import *


class oh_claim_of_right_deduction(Variable):
    value_type = float
    entity = Person
    label = "Ohio deduction for repayment of income reported in a prior year"
    unit = USD
    documentation = (
        "Ohio adjusted gross income deduction for repaying income included in "
        "adjusted gross income in an earlier year under a claim of right "
        "(Schedule of Adjustments, line 29 in 2025). It applies when the "
        "federal return claims the section 1341 credit or deducts the "
        "repayment as an itemized deduction, and excludes income that "
        "qualified for the Ohio resident or nonresident credit in the year it "
        "was received."
    )
    definition_period = YEAR
    reference = (
        # R.C. 5747.01(A)(12)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        # 2025 Ohio IT 1040 instructions, Schedule of Adjustments line 29
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=23",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        claimed = person.tax_unit("claim_of_right_relief_claimed", period)
        repayment = person("claim_of_right_repayment", period)
        credited = person("oh_claim_of_right_repayment_qualified_for_credit", period)
        # Dependents' repayments belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return where(claimed & head_or_spouse, max_(repayment - credited, 0), 0)
