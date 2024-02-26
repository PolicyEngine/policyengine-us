from policyengine_us.model_api import *


class id_grocery_credit_base(Variable):
    value_type = float
    entity = Person
    label = "Idaho base grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7",
    )

    def formula(person, period, parameters):
        return parameters(
            period
        ).gov.states.id.tax.income.credits.grocery.amount.base
