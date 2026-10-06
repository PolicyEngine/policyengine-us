from policyengine_us.model_api import *


class ia_income_tax_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa income tax when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline",
    )
    defined_for = StateCode.IA
    adds = ["ia_base_tax_joint", "ia_amt_joint"]
