from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class sd_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP annualized income limit"
    defined_for = StateCode.SD
    reference = (
        # Pages 1-5 publish three-month limits for sizes 1-15.
        "https://liheapch.acf.gov/docs/2024/benefits-matricies/SD_BenefitMatrix_2024.pdf#page=1",
        "https://dss.sd.gov/economicassistance/energy_weatherization_assistance.aspx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.income
        size = spm_unit("spm_unit_size", period)
        # This component supports wholly qualified households. The citizenship
        # calculator's mixed-status size and income allocation remain unresolved.
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        state = spm_unit.household("state_code_str", period)
        four_person_smi = parameters(period).gov.hhs.smi.amount[state]
        size_share = smi(size, state, period, parameters) / four_person_smi
        smi_limit = np.floor(four_person_smi * p.limits.smi_rate) * size_share
        annual_limit = min_(
            guideline * p.limits.fpg_upper_rate,
            max_(guideline * p.limits.fpg_lower_rate, smi_limit),
        )
        # This inferred ordering matches every FY2024 and published FY2026
        # three-month maximum. Annualize the rounded quarter, not its unrounded
        # annual equivalent. Sizes 11+ carry the FY2024 rule forward; earlier
        # backfilled years are unverified and FY2022 used different rounding.
        return where(size > 0, 4 * np.floor(annual_limit / 4), 0)
