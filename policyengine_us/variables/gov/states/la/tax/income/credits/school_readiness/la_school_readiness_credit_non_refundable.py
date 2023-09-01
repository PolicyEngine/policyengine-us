from policyengine_us.model_api import *


class la_school_readiness_credit_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non-refundable school readiness tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    adds = ["la_school_readiness_tax_credit"]
    subtracts = ["la_school_readiness_tax_credit_refundable"]
