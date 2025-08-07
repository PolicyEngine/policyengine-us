from policyengine_us.model_api import *


class mt_income_tax_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = ["mt_income_tax_before_refundable_credits_joint"]
    subtracts = ["mt_refundable_credits"]
