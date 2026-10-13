from policyengine_us.model_api import *


class oh_claim_of_right_deduction(Variable):
    value_type = float
    entity = Person
    label = "Ohio deduction for repayment of income reported in a prior year"
    unit = USD
    documentation = (
        "Ohio adjusted gross income deduction for repaying income included in "
        "adjusted gross income in an earlier year under a claim of right "
        "(Schedule of Adjustments, line 23 in 2021 and line 29 in 2025), "
        "excluding the part that R.C. 5747.01(A)(12) does not allow. Following "
        "the department's instructions, every edition from 2021, it applies "
        "only when the federal return claims the section 1341 credit or "
        "deducts the repayment as an itemized deduction; the statute itself "
        "requires that the deduction be allowable, not claimed."
    )
    definition_period = YEAR
    reference = (
        # R.C. 5747.01(A)(12)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        # 2021 Ohio IT 1040 instructions, Schedule of Adjustments line 23
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=17",
        # 2025 Ohio IT 1040 instructions, Schedule of Adjustments line 29
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=23",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        claimed = person.tax_unit("claim_of_right_relief_claimed", period)
        repayment = person("claim_of_right_repayment", period)
        excluded = person("oh_claim_of_right_repayment_not_deductible", period)
        # Dependents' repayments belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return where(claimed & head_or_spouse, max_(repayment - excluded, 0), 0)
