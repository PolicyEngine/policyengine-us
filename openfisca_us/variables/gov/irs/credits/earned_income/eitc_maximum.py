from openfisca_us.model_api import *


class eitc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
    unit = USD

    def formula(tax_unit, period, parameters):
        child_count = tax_unit("eitc_child_count", period)
        eitc = parameters(period).gov.irs.credits.eitc
        return eitc.max.calc(child_count)
