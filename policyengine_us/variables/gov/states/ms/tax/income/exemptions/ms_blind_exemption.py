from policyengine_us.model_api import *


class ms_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi blind exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the MS blind exemptions part of the parameter tree.
        p = parameters(period).gov.states.ms.tax.income.exemptions.blind

        # Determine if head of household (filer) is eligible.
        head_eligible = tax_unit("blind_head", period).astype(int)

        # Determine whether spouse is eligible.
        joint = filing_status == filing_status.possible_values.JOINT
        spouse_eligible = (tax_unit("blind_spouse", period) * joint).astype(
            int
        )

        # Calculate total blind exemption.
        return (head_eligible + spouse_eligible) * p.amount
