from policyengine_us.model_api import *


class ia_modified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa modified income used in tax-exempt and alternate-tax calculations"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline#page=55",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline#page=55",
    )
    defined_for = StateCode.IA
    adds = "gov.states.ia.tax.income.modified_income.sources"
