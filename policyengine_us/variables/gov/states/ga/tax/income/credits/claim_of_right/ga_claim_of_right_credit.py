from policyengine_us.model_api import *


class ga_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia claim of right credit"
    unit = USD
    documentation = (
        "When federal tax is computed under 26 U.S.C. 1341(a)(5), the credit "
        "option, Georgia allows a credit for the reduction in the earlier "
        "year's Georgia tax computed as if the repaid income had not been "
        "received. It is reported with Georgia income tax withheld (Form "
        "500, line 25), so any excess over the year's tax is refunded. Under "
        "the deduction option the federal deduction flows to the Georgia "
        "return and there is no credit. Georgia's instructions state the "
        "rule from tax year 2024."
    )
    definition_period = YEAR
    reference = (
        # 2025 IT-511, Form 500 line 25, Claim of right under IRC 1341
        "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=18",
        # 2024 IT-511, same paragraph
        "https://dor.georgia.gov/document/document/2024-it-511-individual-income-tax-booklet/download#page=18",
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        person = tax_unit.members
        decrease = person("ga_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(credit_applies, prior_year_tax_decrease, 0)
