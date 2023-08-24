from policyengine_us.model_api import *


class la_child_tax_credit_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana refundable child expense tax credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = "la_child_tax_credit_refundable_eligible"

    adds = ["la_child_expense_tax_credit"]