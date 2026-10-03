from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ri_liheap_income_band(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Rhode Island LIHEAP benefit income band"
    defined_for = StateCode.RI
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.payment
        size = spm_unit("ri_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        income = spm_unit("ri_liheap_income", period)
        band = np.ones_like(size, dtype=int)
        for rate in p.fpg_rates:
            threshold = np.floor(guideline * rate + 0.5)
            band = band + (income > threshold)
        # Use the published percentage labels. The size-two 125% table cell
        # repeats $31,725 (150%); the labeled 125% rule gives $26,438.
        return where(size > 0, band, 0)
