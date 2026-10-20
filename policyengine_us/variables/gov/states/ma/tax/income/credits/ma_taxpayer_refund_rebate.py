from policyengine_us.model_api import *


class ma_taxpayer_refund_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts taxpayer refund rebate"
    documentation = (
        "One-time Massachusetts Chapter 62F refund paid in 2022 and determined from "
        "tax year 2021 liability. PolicyEngine attributes it to eligibility tax year "
        "2021 through ma_refundable_credits. Its standalone formula can calculate an "
        "amount in other years because the rate persists; it enters the "
        "refundable-credit total only in 2021."
    )
    defined_for = StateCode.MA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62F/Section6",
        "https://www.mass.gov/info-details/chapter-62f-taxpayer-refunds",
    )

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "ma_income_tax_before_refundable_credits", period
        )
        p = parameters(period).gov.states.ma.tax.income.credits

        # Sum refundable credits except ma_taxpayer_refund_rebate to avoid circular reference
        refundable_credit_list = p.refundable
        other_refundable_credits = 0
        for credit in refundable_credit_list:
            if credit != "ma_taxpayer_refund_rebate":
                other_refundable_credits += tax_unit(credit, period)

        income_tax_less_credits = max_(
            income_tax_before_credits - other_refundable_credits, 0
        )
        return p.taxpayer_refund_rebate.rate * income_tax_less_credits
