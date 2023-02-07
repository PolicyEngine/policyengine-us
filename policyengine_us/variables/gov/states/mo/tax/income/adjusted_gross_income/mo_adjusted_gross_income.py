from policyengine_us.model_api import *


class mo_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.121",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        gross_income = person("irs_gross_income", period)
        subtractions = person("mo_qualified_health_insurance_premiums", period)
        return max_(0, gross_income - subtractions)
