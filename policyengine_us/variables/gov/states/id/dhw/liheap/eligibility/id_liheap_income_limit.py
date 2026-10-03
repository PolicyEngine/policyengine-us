from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class id_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP annual income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=8",
        "https://healthandwelfare.idaho.gov/services-programs/financial-assistance/home-heating-and-utility-assistance/apply-heating-assistance",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("id_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        group = spm_unit.household("state_group_str", period)
        p = parameters(period)
        eligibility = p.gov.states.id.dhw.liheap.eligibility
        base = p.gov.hhs.smi.amount[state]
        factor = smi(size, state, period, parameters) / base
        # Flooring the four-person base before applying the size factor matches
        # all seven published FY2026 SMI limits. The source specifies the dollar
        # amounts, not this inferred rounding order. Preserve monthly cents.
        annual_smi = np.floor(np.floor(base * eligibility.smi_rate) * factor)
        monthly_smi = np.round(annual_smi / MONTHS_IN_YEAR, 2)
        annual_fpg = eligibility.fpg_rate * fpg(
            max_(size, 1),
            group,
            period,
            parameters,
            year_lag=eligibility.fpg_year_lag,
        )
        # The plan explicitly switches to FPG at size eight, even though this
        # lowers the limit; using max(SMI, FPG) would contradict its table.
        annual_limit = where(
            size <= eligibility.smi_max_household_size,
            monthly_smi * MONTHS_IN_YEAR,
            annual_fpg,
        )
        return where(size > 0, annual_limit, 0)
