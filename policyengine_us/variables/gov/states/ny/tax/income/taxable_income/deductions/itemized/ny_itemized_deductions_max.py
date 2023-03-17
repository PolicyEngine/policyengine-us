from policyengine_us.model_api import *


class ny_itemized_deductions_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY uncapped itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        gov = parameters(period).gov
        itm_deds = [
            deduction
            for deduction in gov.irs.deductions.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        itm_deds_less_salt = add(tax_unit, period, itm_deds)
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        salt = gov.irs.deductions.itemized.salt_and_real_estate
        cap = salt.cap[tax_unit("filing_status", period)]
        capped_property_taxes = min_(property_taxes, cap)
        capped_tuition = min_(
            gov.states.ny.tax.income.deductions.itemized.college_tuition_max,
            add(tax_unit, period, ["qualified_tuition_expenses"]),
        )
        return itm_deds_less_salt + capped_property_taxes + capped_tuition
