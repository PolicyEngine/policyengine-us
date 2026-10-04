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
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=7",
        "https://www.nj.gov/dca/hmfa/about/regulations/docs/noticeofadoption10.20.25njr.pdf#page=6",
    )
    documentation = "FY2026 handbook and published limits use 60% SMI rather than the codified 175%-FPG ceiling. Chapter 5:49 was readopted without change effective September 22, 2025; its 2017 expiration does not resolve this conflict. This draft follows the operating handbook while legal reconciliation remains open. Annualized monthly limits control this monthly-income eligibility test."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.eligibility
        size = max_(spm_unit("nj_liheap_household_size", period), 1)
        capped_size = min_(size, p.max_table_size)
        state = spm_unit.household("state_code_str", period)
        smi_parameters = parameters(period).gov.hhs.smi
        base = smi_parameters.amount[state]
        factor = smi(capped_size, state, period, parameters) / base
        # Inferred two-stage flooring reproduces all 12 annual limits;
        # their monthly column uses half-up rounding (not half-to-even).
        annual = np.floor(factor * np.floor(base * p.smi_rate))
        monthly = np.floor(annual / MONTHS_IN_YEAR + 0.5)
        # The published monthly increment is rounded up separately. Applying
        # the size factor to the whole household would miss the 13+ rows.
        step = np.ceil(
            base
            * p.smi_rate
            * smi_parameters.household_size_adjustment.additional_person
            / MONTHS_IN_YEAR
        )
        return (monthly + max_(size - p.max_table_size, 0) * step) * MONTHS_IN_YEAR
