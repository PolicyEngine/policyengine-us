from policyengine_us.model_api import *


class ut_taxpayer_credit_reduction(Variable):
    """
    This variable computes the phase-out amount of the Utah tax credit (line 19
    of Utah TC-40 form), which we call the Utah taxpayer credit reduction. It
    is the income subject to phase-out multiplied by the phase out rate.
    """

    value_type = float
    entity = TaxUnit
    label = "UT taxpayer credit reduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        gov = parameters(period).gov
        ut_taxpayer_credit_params_path = (
            gov.states.ut.tax.income.credits.taxpayer_credit
        )
        filing_status = tax_unit("filing_status", period)
        phase_out_start = ut_taxpayer_credit_params_path.phase_out.start[
            filing_status
        ]
        phase_out_rate = ut_taxpayer_credit_params_path.phase_out.rate
        ut_taxable_income = tax_unit("ut_taxable_income", period)
        income_subject_to_phase_out = max(
            ut_taxable_income - phase_out_start, 0
        )
        return income_subject_to_phase_out * phase_out_rate
