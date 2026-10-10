from policyengine_us.model_api import *


class ok_claim_of_right_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma refund of prior-year tax on restored claim of right income"
    unit = USD
    documentation = (
        "Oklahoma has no claim of right credit or deduction of its own for "
        "the year of repayment. When the federal return takes the credit "
        "under 26 U.S.C. 1341(a)(5), Oklahoma recognizes a recomputation of "
        "federal adjusted gross income for the year the income was received: "
        "the filer amends the Oklahoma return for that year to exclude the "
        "repaid income, within one year of filing the federal return that "
        "claims the credit (OAC 710:50-3-9). The refund of that earlier "
        "year's tax is counted here in the year of repayment, the year whose "
        "federal return gives rise to it, as other refunds keyed to an "
        "earlier return are. Under the federal deduction the repayment "
        "flows to Oklahoma itemized deductions and there is no refund."
    )
    definition_period = YEAR
    reference = (
        # OAC 710:50-3-9
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/resources/rules-and-policies/agency-rules/2026/Chapter50-Income-2026.pdf#page=15",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        person = tax_unit.members
        decrease = person("ok_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(credit_applies, prior_year_tax_decrease, 0)
