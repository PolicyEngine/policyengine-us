from policyengine_us.model_api import *


class ca_wftc(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Working Family Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.wftc
        eitc_eligible = tax_unit("eitc_eligible", period)
        caeitc_eligible = tax_unit("ca_eitc_eligible", period)
        eligibility = eitc_eligible | caeitc_eligible
        return p.amount * eligibility
