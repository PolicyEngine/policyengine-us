from policyengine_us.model_api import *


class md_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland IRC section 1341 repayment credit"
    unit = USD
    documentation = (
        "A filer whose federal adjustment for repaying claim of right income "
        "must be made as a credit (26 U.S.C. 1341(a)(5)) makes the Maryland "
        "adjustment as a credit too: the Maryland state and local tax paid "
        "on the repaid income in the year it was received. Any excess over "
        "the year's Maryland state and local income tax is refunded. Under "
        "the federal deduction method there is no credit; the deduction "
        "flows through Maryland itemized deductions."
    )
    definition_period = YEAR
    reference = (
        # Administrative Release No. 40, section IV.B
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/administrative-releases/income-and-estate-tax/ar_it40.pdf#page=3",
        # 2025 Form 502CR, Part CC, line 4
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/502cr.pdf#page=4",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        person = tax_unit.members
        decrease = person("md_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(credit_applies, prior_year_tax_decrease, 0)
