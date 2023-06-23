from policyengine_us.model_api import *


class id_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EIS00407/EIS00407_01-05-2023.pdf"
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf"
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):

        p = parameters(period).gov.states.id.tax.income.deductions.itemized
        itm_deds = [
            deduction
            for deduction in p.amount
            if deduction not in ["salt_deduction"]
        ]
        itm_deds_less_salt = add(tax_unit, period, itm_deds)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        
        return itm_deds_less_salt + uncapped_property_taxes