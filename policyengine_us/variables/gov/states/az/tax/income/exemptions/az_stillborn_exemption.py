from policyengine_us.model_api import *


class az_stillborn_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona stillborn exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions

        stillborn = tax_unit("tax_unit_stillborn_children", period)

        return stillborn * p.stillborn
