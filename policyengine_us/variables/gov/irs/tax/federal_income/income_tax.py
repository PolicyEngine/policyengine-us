from policyengine_us.model_api import *


class income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Federal income tax"
    documentation = "Total federal individual income tax liability."
    adds = [
        "income_tax_before_credits",
    ]
    subtracts = [
        "income_tax_refundable_credits",
        "income_tax_capped_non_refundable_credits",
    ]

    adds = ["income_tax_before_refundable_credits"]
    subtracts = ["income_tax_refundable_credits"]

    def formula(person, period, parameters):
        if parameters(
            period
        ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
            return 0
        else:
            added_components = add(person, period, income_tax.adds)
            subtracted_components = add(person, period, income_tax.subtracts)
            return added_components - subtracted_components
