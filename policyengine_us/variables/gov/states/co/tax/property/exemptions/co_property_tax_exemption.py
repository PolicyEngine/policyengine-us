from policyengine_us.model_api import *


class co_property_tax_exemption(Variable):
    value_type = float
    entity = TaxUnit
    unit = CAD
    label = "Colorado property tax exemption"
    definition_period = YEAR
    defined_for = "co_property_tax_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.exemptions.property_tax
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
