from policyengine_us.model_api import *


class ia_modified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa modified income used in tax-exempt and alternate-tax calculations"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=55"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=55"
    )
    defined_for = StateCode.IA
    adds = "gov.states.ia.tax.income.modified_income.sources"
