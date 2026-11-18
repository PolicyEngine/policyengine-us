from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mn_eap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Minnesota EAP annual income limit"
    defined_for = StateCode.MN
    reference = (
        # PDF pages 88-89
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=88",
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=90",
        "https://liheapch.acf.gov/docs/2026/state-plans/MN_Plan_2026.pdf#page=8",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.commerce.eap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("mn_eap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        state_group = spm_unit.household("state_group_str", period)
        # The tables use 50% of state median income for sizes 1 to 18 and 110%
        # of the prior year's poverty guideline for sizes 19 and 20. The larger
        # of the two reproduces all 40 FFY2026 and FFY2027 monthly cells, and
        # 42 U.S.C. 8624(b)(2)(B) keeps the 110% floor above size 20, where
        # the tables stop. Each monthly cell truncates the annual amount / 12.
        smi_limit = np.floor(
            np.round(smi(size, state, period, parameters) * p.smi_rate, 2)
            / MONTHS_IN_YEAR
        )
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        fpg_limit = np.floor(np.round(guideline * p_hhs.fpg_floor, 2) / MONTHS_IN_YEAR)
        monthly_limit = max_(smi_limit, fpg_limit)
        # Eligibility compares one month of income with the one-month limit,
        # so the annual equivalent is twelve times that limit, not the
        # published annual column.
        return where(size > 0, monthly_limit * MONTHS_IN_YEAR, 0)
