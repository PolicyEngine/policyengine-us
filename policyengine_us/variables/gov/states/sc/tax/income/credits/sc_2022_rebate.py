from policyengine_us.model_api import *


class sc_2022_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina 2022 rebate"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference = "https://www.scstatehouse.gov/sess124_2021-2022/bills/1087.htm"

    def formula(tax_unit, period, parameters):
        tax_before_non_refundable_credits = tax_unit(
            "sc_income_tax_before_non_refundable_credits", period
        )
        p = parameters(period).gov.states.sc.tax.income.credits
        other_non_refundable_credits = 0
        for credit in p.non_refundable:
            if credit != "sc_2022_rebate":
                other_non_refundable_credits += tax_unit(credit, period)
        refundable_credits = tax_unit("sc_refundable_credits", period)
        tax_after_credits = max_(
            0,
            tax_before_non_refundable_credits
            - other_non_refundable_credits
            - refundable_credits,
        )
        return min_(tax_after_credits, p["2022_rebate"].amount)
