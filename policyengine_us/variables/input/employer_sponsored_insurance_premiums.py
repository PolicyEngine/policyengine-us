from policyengine_us.model_api import *


class employer_sponsored_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Employer-sponsored insurance premiums"
    documentation = (
        "Annual employer-paid health insurance premiums. CBO treats this "
        "as part of household market income. Excludes employee-paid premiums, both pretax payroll deductions in pre_tax_health_insurance_premiums and non-pretax payments in the other premium inputs."
    )
    definition_period = YEAR
    unit = USD
    uprating = "calibration.gov.cbo.income_by_source.employment_income"
