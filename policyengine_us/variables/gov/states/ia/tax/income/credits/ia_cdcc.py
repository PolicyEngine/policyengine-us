from policyengine_us.model_api import *


class ia_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf#page=2"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=86"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf#page=2"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=86"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        federal_cdcc = tax_unit("cdcc", period)
        netinc = add(tax_unit, period, ["ia_net_income"])
        p = parameters(period).gov.states.ia.tax.income
        return federal_cdcc * p.credits.child_care.fraction.calc(netinc)
