from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class nj_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP annualized income limit"
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://nj.gov/dca/dhcr/offices/docs/FY2026%20USFHEA%20Factsheet%20-%20English.pdf#page=2",
        "https://nj.gov/dca/dhcr/offices/docs/FY2027%20USFHEA%20Factsheet%20-%20English.pdf#page=2",
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=7",
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=7",
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=2",
        "https://www.nj.gov/dca/hmfa/about/regulations/docs/noticeofadoption10.20.25njr.pdf#page=6",
        "https://www.nj.gov/bpu/newsroom/2021/approved/20211019.html",
    )
    documentation = (
        "The FY2026 and FY2027 handbooks and published limits use 60% SMI rather "
        "than the codified 175%-FPG ceiling. Chapter 5:49 was readopted without "
        "change effective September 22, 2025; the readoption does not reconcile the "
        "conflict, and the model follows the handbooks. The 60% SMI test began in "
        "FY2022 (BPU announcement of October 19, 2021); earlier periods are not "
        "modeled (eligibility/in_effect). Annualized monthly limits control this "
        "monthly-income eligibility test."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.eligibility
        size = max_(spm_unit("nj_liheap_household_size", period), 1)
        state = spm_unit.household("state_code_str", period)
        smi_parameters = parameters(period).gov.hhs.smi
        base = smi_parameters.amount[state]

        def monthly_limit(table_size):
            factor = smi(table_size, state, period, parameters) / base
            # ACF LIHEAP IM 2025-02 Attachment 4 (page 2) floors 60% of the
            # four-person SMI, then floors each size's share of it; the fact
            # sheet's monthly column rounds that half up (not half to even).
            annual = np.floor(factor * np.floor(base * p.smi_rate))
            return np.floor(annual / MONTHS_IN_YEAR + 0.5)

        monthly = monthly_limit(min_(size, p.max_table_size))
        # The fact sheet's increment for each member above the table ($241 for
        # FY2026, $246 for FY2027) is the difference between its last two
        # monthly limits, which rounds the 3% size step where they do.
        step = monthly_limit(p.max_table_size) - monthly_limit(p.max_table_size - 1)
        return (monthly + max_(size - p.max_table_size, 0) * step) * MONTHS_IN_YEAR
