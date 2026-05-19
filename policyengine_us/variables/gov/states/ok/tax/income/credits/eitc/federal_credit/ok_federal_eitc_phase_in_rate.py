from policyengine_us.model_api import *


class ok_federal_eitc_phase_in_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-in rate for the Oklahoma EITC computation"
    unit = "/1"
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    Federal EITC phase-in rate using FROZEN 2020 parameters.

    The phase-in rate determines how quickly the EITC builds up as earnings
    increase. The credit equals earnings * phase_in_rate until the maximum
    credit is reached.

    2020 Phase-in rates by number of children:
    - 0 children: 7.65%
    - 1 child: 34.00%
    - 2 children: 40.00%
    - 3+ children: 45.00%

    Example: Single filer with 2 children and $10,000 earnings
    - Phase-in rate: 40%
    - Phased-in credit: $10,000 * 0.40 = $4,000
    - (Capped at maximum of $5,920 for 2 children)
    """

    def formula(tax_unit, period, parameters):
        child_count = tax_unit("eitc_child_count", period)
        # Use FROZEN 2020 parameters per Oklahoma statute
        eitc = parameters("2020-01-01").gov.irs.credits.eitc
        return eitc.phase_in_rate.calc(child_count)
