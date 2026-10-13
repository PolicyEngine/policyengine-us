from policyengine_us.model_api import *


class in_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana repayment of previously taxed income deduction"
    unit = USD
    documentation = (
        "Indiana deduction for repaying income included in Indiana adjusted "
        "gross income in an earlier year under a claim of right (IT-40 "
        "Schedule 2, code 630). It applies to repayments of any amount, "
        "whether the federal return deducts the repayment, claims the section "
        "1341 credit or takes the standard deduction."
    )
    definition_period = YEAR
    reference = (
        # IC 6-3-1-3.5(a)(22), as amended by HEA 1001-2021, section 71
        "https://www.in.gov/sba/files/HB1001-Final.pdf#page=117",
        # 2018 IT-40 instructions, deduction 630
        "https://forms.in.gov/Download.aspx?id=13952#page=23",
        # 2025 IT-40 instructions, deduction 630
        "https://forms.in.gov/Download.aspx?id=16915#page=23",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        repayment = person("claim_of_right_repayment", period)
        excluded = person("in_claim_of_right_repayment_excluded_from_income", period)
        # Dependents' repayments belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(max_(repayment - excluded, 0) * head_or_spouse)
