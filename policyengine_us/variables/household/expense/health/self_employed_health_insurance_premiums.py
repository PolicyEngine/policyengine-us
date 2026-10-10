from policyengine_us.model_api import *


class self_employed_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance premiums"
    unit = USD
    documentation = (
        "Annual person-paid health insurance premiums for plans covering "
        "individuals not covered by employer-sponsored health insurance. Excludes "
        "pretax payroll deductions and employer-paid premiums; pretax payroll "
        "payments belong only in pre_tax_health_insurance_premiums. The pretax "
        "and non-pretax sets are disjoint. Defaults to the direct non-pretax "
        "health_insurance_premiums input for self-employed people."
    )
    definition_period = YEAR
    defined_for = "is_self_employed"
    adds = ["health_insurance_premiums"]
