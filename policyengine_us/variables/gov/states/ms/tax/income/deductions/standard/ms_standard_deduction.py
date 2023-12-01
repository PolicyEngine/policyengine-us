from policyengine_us.model_api import *


class ms_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi personal standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the MS Standard Deduction part of the parameter tree.
        p = parameters(period).gov.states.ms.tax.income.deductions.standard

        # Get their standard deduction amount based on their filing status.
        return p.amount[filing_status]
