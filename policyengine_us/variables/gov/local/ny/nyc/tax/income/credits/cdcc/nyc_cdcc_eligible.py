from policyengine_us.model_api import *


class nyc_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for NYC CDCC"
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # Eligibility is based on having a federal AGI below $30k
        # and being an NYC full-time resident.

        # First get their income.
        income = tax_unit("adjusted_gross_income", period)

        # Then get the CDCC part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.cdcc

        return income <= p.phaseout_end
