from openfisca_us.model_api import *


class lives_with_joint_filing_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Indicates whether the tax filing head lived with their joint-filing spouse the entire year. False if not married filing jointly."

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        return filing_status == filing_status.possible_values.JOINT
