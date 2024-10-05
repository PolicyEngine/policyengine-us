from policyengine_us.model_api import *


class id_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        qualified_months = person("id_grocery_credit_qualified_months", period)
        full_amount = add(
            person,
            period,
            ["id_grocery_credit_base", "id_grocery_credit_aged"],
        )
        credit_value = full_amount * (qualified_months / MONTHS_IN_YEAR)
        return tax_unit.sum(credit_value)
