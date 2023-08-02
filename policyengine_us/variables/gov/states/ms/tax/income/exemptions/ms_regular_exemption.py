from policyengine_us.model_api import *


class ms_regular_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi regular exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the MS Exemptions part of the parameter tree.
        p = parameters(period).gov.states.ms.tax.income.exemptions

        # Get their regular exemption amount based on their filing status.
        return p.regular.amount[filing_status]
