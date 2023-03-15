from policyengine_us.model_api import *


class nj_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey blind or disabled exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the NJ blind ir disabled exemptions part of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exemptions.blind

        # Get the individual blind status.
        blind_head = tax_unit("blind_head", period).astype(int)

        # Determine whether spouse is eligible.
        joint = filing_status == filing_status.possible_values.JOINT
        blind_spouse = (tax_unit("blind_spouse", period) * joint).astype(int)

        # Calculate total blind exemption.
        return (blind_head + blind_spouse) * p.amount
