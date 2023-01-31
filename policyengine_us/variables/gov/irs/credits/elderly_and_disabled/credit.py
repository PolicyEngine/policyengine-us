from policyengine_us.model_api import *


class elderly_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Elderly or disabled credit"
    documentation = "Schedule R credit for the elderly and the disabled"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/22"

    def formula(tax_unit, period, parameters):
        elderly_disabled = parameters(
            period
        ).gov.irs.credits.elderly_or_disabled
        return elderly_disabled.rate * tax_unit("section_22_income", period)


c07200 = variable_alias("c07200", elderly_disabled_credit)
