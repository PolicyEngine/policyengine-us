from policyengine_us.model_api import *


class de_aged_personal_credit_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware aged personal credit per person for combined separate filing"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=9",
        "https://delcode.delaware.gov/title30/c011/sc02/index.html#1110",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # PIT-RES Line 27b: "If you are filing a combined separate
        # return (Filing Status 4), enter $110 in the column(s) that
        # correspond to the checked box(es)."  Aged credit is locked
        # to the person's column.
        p = parameters(period).gov.states.de.tax.income.credits.personal_credits
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        return is_head_or_spouse * p.aged.calc(age)
