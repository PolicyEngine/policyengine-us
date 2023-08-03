from policyengine_us.model_api import *


class ca_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA income tax"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/Search/Home/Confirmation"

    adds = [
        "ca_income_tax_before_refundable_credits",
        "ca_mental_health_services_tax",
        "ca_use_tax",
    ]
    subtracts = ["ca_refundable_credits"]
