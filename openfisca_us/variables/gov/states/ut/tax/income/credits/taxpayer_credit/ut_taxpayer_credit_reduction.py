from openfisca_us.model_api import *


class ut_taxpayer_credit_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT taxpayer credit reduction"
    unit = USD
    definition_period = YEAR

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
