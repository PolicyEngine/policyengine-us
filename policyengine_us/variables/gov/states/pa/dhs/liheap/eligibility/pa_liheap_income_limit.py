from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class pa_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP opening-season annual income limit"
    defined_for = StateCode.PA
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=10",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.liheap.eligibility
        size = spm_unit("pa_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1),
            state_group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        # This annual opening-season snapshot matches FY2026 and FY2027.
        # Pennsylvania updates guidelines midseason; annual inputs cannot
        # select a later application-month limit. Earlier backfills are unverified.
        return where(size > 0, guideline * p.fpg_rate, 0)
