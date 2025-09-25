from policyengine_us.model_api import *


class in_automatic_refund_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana automatic refund rebate"
    defined_for = StateCode.IN
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/indiana/2022/title-4/article-10/chapter-22/"

    def formula(tax_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.credits.automatic_refund_rebate.amount
        )

        # Total amount per person (base + additional)
        amount_per_person = p.base + p.additional

        # Multiply by number of head and spouse
        head_spouse_count = tax_unit("head_spouse_count", period)

        return amount_per_person * head_spouse_count
