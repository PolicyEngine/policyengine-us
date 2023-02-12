from policyengine_us.model_api import *


class md_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        us_itemizer = tax_unit("tax_unit_itemizes", period)
        md_std_ded = tax_unit("md_standard_deduction", period)
        p = parameters(period).gov.irs.deductions
        us_deductions_if_itemizing = [
            deduction
            for deduction in p.deductions_if_itemizing
            if deduction
            not in [
                "salt_deduction",
                "qualified_business_income_deduction",
            ]
        ]
        us_itemized_deductions_less_salt = add(
            tax_unit, period, us_deductions_if_itemizing
        )
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        salt = p.itemized.salt_and_real_estate
        cap = salt.cap[tax_unit("filing_status", period)]
        capped_property_taxes = min_(property_taxes, cap)
        md_itm_ded = us_itemized_deductions_less_salt + capped_property_taxes
        return where(
            us_itemizer,
            where(md_itm_ded > md_std_ded, md_itm_ded, md_std_ded),
            md_std_ded,
        )
