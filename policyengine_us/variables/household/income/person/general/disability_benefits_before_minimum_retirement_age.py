from policyengine_us.model_api import *


class disability_benefits_before_minimum_retirement_age(Variable):
    value_type = float
    entity = Person
    label = "disability benefits before minimum retirement age"
    unit = USD
    documentation = (
        "Taxable benefits received under an employer's disability retirement "
        "plan before the plan's minimum retirement age, reported as wages on "
        "Form 1040 line 1h. They are earned income until that age. Railroad "
        "retirement benefits, including disability benefits, are not. "
        "Defaults to zero."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.employment_income"
    reference = (
        "https://www.irs.gov/pub/irs-prior/p596--2024.pdf#page=8",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=18",
    )
