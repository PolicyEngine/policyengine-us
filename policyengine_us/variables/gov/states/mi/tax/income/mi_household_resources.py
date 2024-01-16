from policyengine_us.model_api import *


class mi_household_resources(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = "https://law.justia.com/codes/michigan/2022/chapter-206/statute-act-281-of-1967/division-281-1967-1/division-281-1967-1-9/section-206-508/"
    adds = "gov.states.mi.tax.income.household_resources"
    subtracts = ["health_insurance_premiums"]
