from policyengine_us.model_api import *


class nj_blind_or_disabled_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey blind or disabled exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Determine whether spouse is eligible.
        joint = filing_status == filing_status.possible_values.JOINT

        # Then get the NJ blind ir disabled exemptions part of the parameter tree.
        p = parameters(
            period
        ).gov.states.nj.tax.income.exemptions.blind_or_disabled

        # Get the individual blind status and disabled.
        blind_head = tax_unit("blind_head", period)
        disabled_head = tax_unit("disabled_head", period)

        # Check if the individual's eligiblity.
        head_eligible = (blind_head | disabled_head).astype(int)

        # Get the individual's spouse blind status and disabled.
        blind_spouse = tax_unit("blind_spouse", period) * joint
        disabled_spouse = tax_unit("disabled_spouse", period)

        # Check if the individual spouse's eligiblity.
        spouse_eligible = (blind_spouse | disabled_spouse).astype(int)

        # Calculate total blind exemption.
        return (head_eligible + spouse_eligible) * p.amount
