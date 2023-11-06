from policyengine_us.model_api import *


class nyc_cdcc_applicable_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC CDCC rate"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # Calculate the "applicable percentage" of the portion of the NYS CDCC
        # applied for children under age four.
        # Up to $25k, the percentage is 75%. Above $25k, it phases out to 0% above $30k.
        # See https://codelibrary.amlegal.com/codes/newyorkcity/latest/NYCadmin/0-0-0-13608
        # § 11-1706 Credits against tax (e).

        # First get federal AGI.
        income = tax_unit("adjusted_gross_income", period)

        # Then get the CDCC part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.cdcc

        phase_out_width = p.phaseout_end - p.phaseout_start
        excess = max_(income - p.phaseout_start, 0)
        capped_excess = min_(excess, phase_out_width)
        percent_excess = capped_excess / phase_out_width
        return p.max_rate * (1 - percent_excess)
