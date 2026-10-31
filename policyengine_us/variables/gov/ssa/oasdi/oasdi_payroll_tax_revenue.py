from policyengine_us.model_api import *


class oasdi_payroll_tax_revenue(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "OASDI modeled payroll tax liability"
    documentation = (
        "Modeled OASDI liability on this person's covered earnings: the "
        "employee and employer FICA shares on wages up to the wage base and "
        "the SECA OASDI tax on self-employment earnings in the remaining room. "
        "A reform that replaces one of these leaves arrives through that leaf; "
        "the owners' draw reform adds its OASDI tax inside the SECA leaf, so "
        "it is counted once. employer_total_social_security_tax is excluded: "
        "it applies the employer rate to a separate employer-aggregate "
        "earnings input, another measure of the employer share already "
        "counted here, not a fourth stream. A modeled liability, not a "
        "trust-fund receipt."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/3101#a",
        "https://www.law.cornell.edu/uscode/text/26/3111#a",
        "https://www.law.cornell.edu/uscode/text/26/1401#a",
    )
    adds = [
        "employee_social_security_tax",
        "employer_social_security_tax",
        "self_employment_social_security_tax",
    ]
