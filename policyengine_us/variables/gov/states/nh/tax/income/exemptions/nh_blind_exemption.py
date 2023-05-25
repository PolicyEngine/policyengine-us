from policyengine_us.model_api import *


class nh_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire blind exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Determine whether spouse is eligible.
        joint = filing_status == filing_status.possible_values.JOINT

        p = parameters(period).gov.states.nh.tax.income.exemptions.amount

        # Get the individual blind status.
        blind_head = tax_unit("blind_head", period)

        # Check if the individual's eligiblity.
        head_eligible = (blind_head).astype(int)

        # Get the individual's spouse blind status.
        blind_spouse = tax_unit("blind_spouse", period) * joint

        # Check if the individual spouse's eligiblity.
        spouse_eligible = (blind_spouse).astype(int)

        # Calculate total blind exemption.
        return (head_eligible + spouse_eligible) * p.blind_addition
