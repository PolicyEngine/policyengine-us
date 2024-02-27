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
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        capped_property_taxes = tax_unit("capped_property_taxes", period)
        p = parameters(period).gov.states.ny.tax.income
        capped_tuition = min_(
            p.deductions.itemized.college_tuition_max,
            add(tax_unit, period, ["qualified_tuition_expenses"]),
        )
        return itm_deds_less_salt + capped_property_taxes + capped_tuition
