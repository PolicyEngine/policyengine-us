from policyengine_us.model_api import *


class id_grocery_credit_qualified_months(Variable):
    value_type = int
    entity = Person
    label = "Months qualified for the Idaho grocery credit"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7",
    )

    def formula(person, period, parameters):
        qualifying_months_sum = 0
        year = period.start.year
        for month in range(1, 13):
            monthly_period_str = f"{year}-{month:02d}"
            qualifying_months_sum += person(
                "id_grocery_credit_qualifying_month", monthly_period_str
            )
        return qualifying_months_sum
