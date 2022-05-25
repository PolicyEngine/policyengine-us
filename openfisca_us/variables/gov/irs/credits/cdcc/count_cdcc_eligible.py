from openfisca_us.model_api import *


class count_cdcc_eligible(Variable):
    value_type = int
    entity = TaxUnit
    label = "CDCC-eligible children"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        num_eligible = add(tax_unit, period, ["cdcc_eligible"])
        max_eligible = parameters(period).irs.credits.cdcc.eligibility.max
        return min_(num_eligible, max_eligible)
