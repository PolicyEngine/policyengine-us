from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class id_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP annual income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=8",
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=1",
        "https://healthandwelfare.idaho.gov/services-programs/financial-assistance/home-heating-and-utility-assistance/apply-heating-assistance",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("id_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        group = spm_unit.household("state_group_str", period)
        p = parameters(period)
        eligibility = p.gov.states.id.dhw.liheap.eligibility
        # The shared helper's flooring order matches all seven HHS FY2026 amounts.
        # DHW prints monthly limits in cents. At sizes 2 and 6 they annualize 4 cents
        # above those amounts, the federal maximum, so the cap applies there.
        annual_smi = liheap_smi_limit(
            size, state, eligibility.smi_rate, period, parameters
        )
        monthly_smi = np.round(annual_smi / MONTHS_IN_YEAR, 2)
        annual_fpg = eligibility.fpg_rate * fpg(
            size,
            group,
            period,
            parameters,
            year_lag=eligibility.fpg_year_lag,
        )
        # The plan explicitly switches to FPG at size eight, even though this
        # lowers the limit; using max(SMI, FPG) would contradict its table.
        annual_limit = where(
            size <= eligibility.smi_max_household_size,
            min_(monthly_smi * MONTHS_IN_YEAR, annual_smi),
            annual_fpg,
        )
        return where(size > 0, annual_limit, 0)
