from policyengine_us.model_api import *


class ctc_qualifying_children(Variable):
    value_type = bool
    entity = TaxUnit
    label = "CTC-qualifying children"
    documentation = "Count of children that qualify for the Child Tax Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        qualifies = person("ctc_child_individual_maximum", period) > 0
        return tax_unit.sum(qualifies)
