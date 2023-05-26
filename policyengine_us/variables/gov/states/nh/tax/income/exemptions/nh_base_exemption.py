from policyengine_us.model_api import *


class nh_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire base exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        joint = filing_status == filing_status.possible_values.JOINT

        # get the NH Exemptions part of the parameter tree.
        p = parameters(period).gov.states.nh.tax.income.exemptions.amount

        # Get their base exemption amounts
        return where(joint, 2 * p.base, p.base)
