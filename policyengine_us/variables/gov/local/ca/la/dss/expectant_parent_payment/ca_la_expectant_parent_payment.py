from policyengine_us.model_api import *


class ca_la_expectant_parent_payment(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Los Angeles County expectant parent payment"
    defined_for = "ca_la_expectant_parent_payment_eligible"

    adds = ["gov.local.ca.la.dss.expectant_parent_payment.amount"]
