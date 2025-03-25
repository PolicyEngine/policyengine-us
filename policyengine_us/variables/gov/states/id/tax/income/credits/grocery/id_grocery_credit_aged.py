from policyengine_us.model_api import *


class id_grocery_credit_aged(Variable):
    value_type = float
    entity = Person
    label = "Idaho aged grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.grocery.aged
        # Aged head and spouse are eligible for an additional grocery credit amount
        age = person("age", period)
        aged = age >= p.age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return aged * head_or_spouse * p.amount
