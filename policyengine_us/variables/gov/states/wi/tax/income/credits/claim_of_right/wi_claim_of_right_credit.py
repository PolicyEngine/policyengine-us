from policyengine_us.model_api import *


class wi_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin claim of right credit"
    unit = USD
    documentation = (
        "The decrease in the earlier year's Wisconsin tax from subtracting "
        "income taxed that year under the claim of right doctrine and "
        "repaid this year, when the repayment exceeds the threshold and is "
        "not subtracted in computing Wisconsin adjusted gross income (Wis. "
        "Stat. 71.07(1)). Any excess over the year's tax is paid to the "
        "filer. Reported on Form 1, line 32. A filer who takes the "
        "retirement income exclusion may claim no credit under Wis. Stat. "
        "71.07 (71.05(6)(b)54m.d), which wi_income_tax applies."
    )
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/1",
        # 2025 Form 1 instructions, line 32
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("wi_claim_of_right_eligible", period)
        credit_applies = tax_unit("wi_claim_of_right_credit_applies", period)
        person = tax_unit.members
        decrease = person("wi_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(eligible & credit_applies, prior_year_tax_decrease, 0)
