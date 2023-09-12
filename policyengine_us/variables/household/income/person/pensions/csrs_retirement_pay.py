from policyengine_us.model_api import *


class csrs_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "Civil Service Retirement System (CSRS) retirement income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Retirement income from the federal Civil Service Retirement System."
    )
    reference = "https://tax.vermont.gov/individuals/seniors-and-retirees"  # Exemption for Civil Service Retirement System (CSRS)
