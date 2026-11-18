from policyengine_us.model_api import *


class hi_adjusted_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii adjusted tax liability"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # HRS 235-91.5: refundable credits are used first, followed by
        # nonrefundable credits.
        "https://www.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0091_0005.htm",
        # Form N-11, line 34: line 27 (tax) minus line 33 (total refundable
        # credits). The result can be negative.
        "https://files.hawaii.gov/tax/forms/2018/n11_i.pdf#page=3",
        "https://files.hawaii.gov/tax/forms/2025/n11_i.pdf#page=3",
        # Nonrefundable credits cannot exceed line 34; none apply when line 34
        # is zero or less.
        "https://files.hawaii.gov/tax/forms/2018/n11ins.pdf#page=25",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=21",
        # Act 115 refunds were issued to 2021 Form N-11 filers by the
        # department, not claimed on the return.
        "https://files.hawaii.gov/tax/news/announce/ann22-03.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        tax = tax_unit("hi_income_tax_before_non_refundable_credits", period)
        refundable_credits = tax_unit("hi_refundable_credits", period)
        # Lines 28 to 33 hold only refundable credits claimed on the return,
        # so the Act 115 refund does not reduce the adjusted tax liability.
        p = parameters(period).gov.states.hi.tax.income.credits
        if "hi_act_115_rebate" in p.refundable:
            refundable_credits = refundable_credits - tax_unit(
                "hi_act_115_rebate", period
            )
        return tax - refundable_credits
