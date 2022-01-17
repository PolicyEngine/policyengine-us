from openfisca_us.model_api import *


class ctc_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "CTC-eligible children"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(tax_unit, period, parameters):
        return tax_unit.sum(tax_unit.members("is_ctc_child_eligible", period))
