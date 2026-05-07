from policyengine_us.model_api import *


class ok_federal_eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Federal earned income credit for the Oklahoma EITC computation"
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    unit = USD
    defined_for = "ok_federal_eitc_eligible"
    documentation = """
    Federal EITC amount computed using FROZEN 2020 parameters for Oklahoma.

    Per 68 O.S. Section 2357.43, Oklahoma calculates its state EITC based on
    the federal EITC parameters that were in effect for tax year 2020. This
    variable computes what the federal EITC would be using those frozen
    parameters, regardless of the current tax year.

    This is the base amount that Oklahoma then multiplies by 5% to get the
    state credit (see ok_eitc variable).

    The formula follows the standard EITC structure:
    1. Phase-in: Credit builds up as earnings increase (at phase_in_rate)
    2. Plateau: Credit stays at maximum for a range of incomes
    3. Phase-out: Credit reduces as income exceeds phase_out_start

    Credit = min(phased_in_amount, maximum - reduction)

    Where:
    - phased_in_amount = earnings * phase_in_rate (capped at maximum)
    - reduction = phase_out_rate * (income - phase_out_start) if income > start

    2020 Federal EITC Parameters (frozen for Oklahoma):
    Children | Maximum  | Phase-in Rate | Phase-out Rate | Phase-out Start
    ---------|----------|---------------|----------------|----------------
    0        | $538     | 7.65%         | 7.65%          | $8,790
    1        | $3,584   | 34.00%        | 15.98%         | $19,330
    2        | $5,920   | 40.00%        | 21.06%         | $19,330
    3+       | $6,660   | 45.00%        | 21.06%         | $19,330
    """

    def formula(tax_unit, period, parameters):
        takes_up_eitc = tax_unit("takes_up_eitc", period)
        # Get maximum credit (using frozen 2020 parameters)
        maximum = tax_unit("ok_federal_eitc_maximum", period)
        # Get phased-in amount based on earnings
        phased_in = tax_unit("ok_federal_eitc_phased_in", period)
        # Get reduction based on income above phase-out threshold
        reduction = tax_unit("ok_federal_eitc_reduction", period)
        # Credit is limited by both phase-in and phase-out
        limitation = max_(0, maximum - reduction)
        return min_(phased_in, limitation) * takes_up_eitc
