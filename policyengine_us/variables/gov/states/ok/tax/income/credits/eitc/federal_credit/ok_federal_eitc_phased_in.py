from policyengine_us.model_api import *


class ok_federal_eitc_phased_in(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-in amount for the Oklahoma EITC computation"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK
    documentation = """
    EITC phase-in amount using FROZEN 2020 parameters.

    The phase-in amount represents how much credit has been "earned" based
    on the filer's adjusted earnings. It equals:
    min(maximum_credit, earnings * phase_in_rate)

    This creates the rising portion of the EITC where the credit increases
    as earnings increase, until the maximum credit is reached.

    Example: Single filer with 1 child and $8,000 earnings (2020 params)
    - Phase-in rate: 34%
    - Maximum credit: $3,584
    - Phased-in amount: min($3,584, $8,000 * 0.34) = min($3,584, $2,720)
    - Result: $2,720 (still phasing in, below maximum)

    Example: Single filer with 1 child and $15,000 earnings (2020 params)
    - Phase-in rate: 34%
    - Maximum credit: $3,584
    - Phased-in amount: min($3,584, $15,000 * 0.34) = min($3,584, $5,100)
    - Result: $3,584 (capped at maximum)
    """

    def formula(tax_unit, period, parameters):
        # Get the maximum credit (frozen at 2020 values)
        maximum = tax_unit("ok_federal_eitc_maximum", period)
        # Get the phase-in rate (frozen at 2020 values)
        phase_in_rate = tax_unit("ok_federal_eitc_phase_in_rate", period)
        earnings = tax_unit("filer_adjusted_earnings", period)
        # Calculate phased-in amount, capped at maximum
        phased_in_amount = earnings * phase_in_rate
        return min_(maximum, phased_in_amount)
