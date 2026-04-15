from policyengine_us.model_api import *


class employer_sponsored_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Employer-sponsored insurance premiums"
    documentation = (
        "Annual employer-paid health insurance premiums. CBO treats this "
        "as part of household market income."
    )
    definition_period = YEAR
    unit = USD
    uprating = "calibration.gov.cbo.income_by_source.employment_income"
