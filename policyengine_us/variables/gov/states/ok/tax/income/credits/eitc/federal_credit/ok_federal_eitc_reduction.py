from policyengine_us.model_api import *


class ok_federal_eitc_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC reduction for the Oklahoma EITC computation"
    unit = USD
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    EITC phase-out reduction using FROZEN 2020 parameters.

    The reduction represents how much the EITC is reduced due to income
    exceeding the phase-out start threshold. It equals:
    phase_out_rate * max(0, income - phase_out_start)

    Where income is the greater of earnings or AGI.

    Example: Single filer with 2 children, $35,000 AGI (2020 params)
    - Phase-out start: $19,330
    - Phase-out rate: 21.06%
    - Excess income: max(0, $35,000 - $19,330) = $15,670
    - Reduction: $15,670 * 0.2106 = $3,300
    - (This reduces the maximum credit of $5,920 to $2,620)

    Example: Joint filers with 2 children, $30,000 AGI (2020 params)
    - Phase-out start: $19,330 + $5,980 (joint bonus) = $25,310
    - Phase-out rate: 21.06%
    - Excess income: max(0, $30,000 - $25,310) = $4,690
    - Reduction: $4,690 * 0.2106 = $988
    """

    def formula(tax_unit, period, parameters):
        earnings = tax_unit("filer_adjusted_earnings", period)
        agi = tax_unit("adjusted_gross_income", period)
        # Use the greater of earnings or AGI for phase-out
        highest_income_variable = max_(earnings, agi)
        # Get phase-out threshold (frozen at 2020 values)
        phase_out_start = tax_unit("ok_federal_eitc_phase_out_start", period)
        phase_out_rate = tax_unit("ok_federal_eitc_phase_out_rate", period)
        # Calculate reduction based on income exceeding threshold
        phase_out_region = max_(0, highest_income_variable - phase_out_start)
        return phase_out_rate * phase_out_region
