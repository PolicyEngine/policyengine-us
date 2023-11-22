from policyengine_us.model_api import *


class mt_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7"
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/"
        # MT Code § 15-30-2131 (2022) (1)
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction", "casualty_loss_deduction"]
        ]
        filing_status = tax_unit("filing_status", period)
        us_itm_deds_less_salt = add(tax_unit, period, itm_deds) + tax_unit(
            "mt_misc_deductions", period
        )
        capped_property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            p.itemized.salt_and_real_estate.cap[filing_status],
        )

        return us_itm_deds_less_salt + capped_property_taxes
