from policyengine_us.model_api import *


class ar_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas Child and Dependent Care Credit"
    unit = USD
    documentation = "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-502/"
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.credits.cdcc
        cdcc = tax_unit("cdcc", period)
        return cdcc * p.match
