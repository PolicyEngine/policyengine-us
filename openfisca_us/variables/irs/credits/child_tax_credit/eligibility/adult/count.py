from openfisca_us.model_api import *


class ctc_eligible_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "ODC-eligible adult dependents"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#h_4"

    def formula(tax_unit, period, parameters):
        return tax_unit.sum(tax_unit.members("is_ctc_adult_eligible", period))
