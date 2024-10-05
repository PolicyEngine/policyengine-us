from policyengine_us.model_api import *


class ut_taxpayer_credit_phase_out_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxpayer credit phase-out income"
    unit = USD
    documentation = (
        "Income that reduces the Utah taxpayer credit. Form TC-40, line 18"
    )
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        thresholds = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.phase_out.threshold
        threshold = thresholds[filing_status]
        income = tax_unit("ut_taxable_income", period)
        return max_(income - threshold, 0)
