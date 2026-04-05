from policyengine_us.model_api import *


class employer_local_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer local payroll tax"
    documentation = (
        "Employer-side local and regional payroll taxes, aggregated from "
        "jurisdiction-specific rules."
    )
    definition_period = YEAR
    unit = USD
    adds = ["ny_mctmt_employer_tax"]
