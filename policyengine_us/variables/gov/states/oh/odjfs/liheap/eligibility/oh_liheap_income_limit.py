from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class oh_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Ohio HEAP annual income limit"
    defined_for = StateCode.OH
    reference = (
        "https://www.clevelandohio.gov/sites/clevelandohio/files/aging/Home%20repair%20Applications/2025-2026_HEAP_application_B_W.pdf#page=1",
        "https://www.lccaa.net/wp-content/uploads/2026/07/2026-2027-EAP-Application-7-2026.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.odjfs.liheap.eligibility
        size = spm_unit("oh_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        state = spm_unit.household("state_code_str", period)
        guideline = fpg(
            max_(size, 1),
            state_group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        # Flooring reproduces the printed FPG amounts: sizes 1-8 for the
        # 2025-26 application and 1-7 for 2026-27. Larger units use 60% SMI.
        # The 2026-27 Consumers' Counsel fact sheet's larger-household dollar
        # figures do not reconcile to the current federal SMI. Use the state
        # application's express percentage; whole-dollar flooring remains an
        # annual approximation, not a verified large-household dollar table.
        limit = where(
            size <= p.maximum_fpg_household_size,
            guideline * p.fpg_rate,
            smi(size, state, period, parameters) * p.smi_rate,
        )
        return where(size > 0, np.floor(limit), 0)
