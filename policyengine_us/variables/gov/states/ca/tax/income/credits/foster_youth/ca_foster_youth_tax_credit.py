from policyengine_us.model_api import *


class ca_foster_youth_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "California foster youth tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "ca_eitc_eligible"

    adds = ["ca_foster_youth_tax_credit_person"]
