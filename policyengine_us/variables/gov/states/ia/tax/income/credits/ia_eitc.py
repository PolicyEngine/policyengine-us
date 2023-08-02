from policyengine_us.model_api import *


class ia_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa earned income tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf#page=2"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=87"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf#page=2"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=87"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("earned_income_tax_credit", period)
        p = parameters(period).gov.states.ia.tax.income
        return federal_eitc * p.credits.earned_income.fraction
