from policyengine_us.model_api import *


class wv_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia Child and Dependent Care Credit"
    unit = USD
    defined_for = StateCode.WV
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-26/"

    def formula(tax_unit, period, parameters):
        # West Virginia matched the federal credit taken
        cdcc = tax_unit("cdcc", period)
        p = parameters(period).gov.states.wv.tax.income.credits.cdcc
        return cdcc * p.match
