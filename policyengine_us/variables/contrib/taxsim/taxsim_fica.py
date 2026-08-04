from policyengine_us.model_api import *


class taxsim_fica(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total FICA: employer and employee OASDI/HI taxes plus SECA"
    unit = USD
    definition_period = YEAR
    reference = "https://taxsim.nber.org/taxsim35/"

    adds = [
        "employee_social_security_tax",
        "employee_medicare_tax",
        "additional_medicare_tax",
        "employer_social_security_tax",
        "employer_medicare_tax",
        "self_employment_tax",
    ]
