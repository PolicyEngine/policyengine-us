from policyengine_us.model_api import *


class bonus_guaranteed_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Bonus guaranteed deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://waysandmeans.house.gov/malliotakis-steel-lead-legislation-to-provide-tax-relief-to-working-families/"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        wftca = parameters(
            period
        ).gov.contrib.congress.wftca.bonus_guaranteed_deduction
        amount = wftca.amount[filing_status]
        agi = tax_unit("adjusted_gross_income", period)
        threshold = wftca.phase_out.threshold[filing_status]
        income_in_phase_out_region = max_(agi - threshold, 0)
        reduction = wftca.phase_out.rate * income_in_phase_out_region
        return max_(amount - reduction, 0)
