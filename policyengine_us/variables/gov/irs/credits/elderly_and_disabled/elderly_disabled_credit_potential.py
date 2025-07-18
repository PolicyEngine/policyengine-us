from policyengine_us.model_api import *


class elderly_disabled_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Potential value of the Elderly or disabled credit"
    documentation = "Schedule R credit for the elderly and the disabled"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/22"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.elderly_or_disabled
        return p.rate * tax_unit("section_22_income", period)
