from policyengine_us.model_api import *


class ok_federal_eitc_phase_out_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-out rate for the Oklahoma EITC computation"
    unit = "/1"
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    Federal EITC phase-out rate using FROZEN 2020 parameters.

    The phase-out rate determines how quickly the EITC reduces as income
    exceeds the phase-out start threshold. The reduction equals:
    phase_out_rate * (income - phase_out_start)

    2020 Phase-out rates by number of children:
    - 0 children: 7.65%
    - 1 child: 15.98%
    - 2 children: 21.06%
    - 3+ children: 21.06%

    Example: Single filer with 1 child and $30,000 income
    - Phase-out start: $19,330
    - Phase-out rate: 15.98%
    - Excess income: $30,000 - $19,330 = $10,670
    - Reduction: $10,670 * 0.1598 = $1,705
    """

    def formula(tax_unit, period, parameters):
        # Use FROZEN 2020 parameters per Oklahoma statute
        eitc = parameters("2020-01-01").gov.irs.credits.eitc
        num_children = tax_unit("eitc_child_count", period)
        return eitc.phase_out.rate.calc(num_children)
