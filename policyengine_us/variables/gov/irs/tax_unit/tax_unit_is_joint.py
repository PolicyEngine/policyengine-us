from policyengine_us.model_api import *


class tax_unit_is_joint(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Is joint-filing tax unit"
    documentation = "Whether this tax unit is a joint filer."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        return filing_status == filing_status.possible_values.JOINT
