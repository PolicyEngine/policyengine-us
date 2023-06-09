from policyengine_us.model_api import *


class nh_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire base exemption household level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        
        # Get members in the tax unit
        person = tax_unit.members

        # Get exemption amount for members
        base = person("nh_person_base_exemption", period)

        return tax_unit.sum(base)