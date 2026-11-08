from policyengine_us.model_api import *


class nj_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employer additional state payroll tax"
    documentation = (
        "Employer-side New Jersey payroll contributions beyond unemployment "
        "insurance: temporary disability insurance and the workforce funds."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ
    adds = [
        "nj_employer_temporary_disability_insurance_contribution",
        "nj_employer_workforce_fund_contribution",
    ]
