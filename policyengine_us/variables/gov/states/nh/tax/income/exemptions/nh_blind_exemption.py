from policyengine_us.model_api import *


class nh_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire blind exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nh.tax.income.exemptions.amount

        # Get the individual blind status.
        blind_head = tax_unit("blind_head", period).astype(int)

        # Get the individual's spouse blind status.
        blind_spouse = tax_unit("blind_spouse", period).astype(int)

        # Calculate total blind exemption.
        return (blind_head + blind_spouse) * p.blind_addition
