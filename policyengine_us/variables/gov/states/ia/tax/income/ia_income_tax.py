from policyengine_us.model_api import *


class ia_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
    )
    defined_for = StateCode.IA
    adds = ["ia_income_tax_before_refundable_credits"]
    subtracts = ["ia_refundable_credits"]
