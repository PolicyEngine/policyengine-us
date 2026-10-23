from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class wi_wheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wisconsin WHEAP regular heating benefit"
    defined_for = "wi_wheap_eligible"
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/16/i/27",
        # Section 2.3.1.
        "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=26",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/WI_BenefitMatrix_2026.xlsx",
        "https://liheapch.acf.gov/docs/2026/state-plans/WI_Plan_2026.pdf#page=5",
        "https://web.archive.org/web/20260316195114/https://energyandhousing.wi.gov/Documents/WHEAP/LiheapPlan_FFY2026.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.doa.wheap
        payment = p.payment
        size = spm_unit("wi_wheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            size, state_group, period, parameters, year_lag=p.eligibility.fpg_year_lag
        )
        income = spm_unit("wi_wheap_countable_income", period)
        limit = spm_unit("wi_wheap_income_limit", period)
        # Categorically eligible households above the limit are paid as if
        # their income equaled it.
        categorical = spm_unit("wi_wheap_categorically_eligible", period)
        benefit_income = where(categorical, min_(income, limit), income)
        poverty_ratio = np.clip(
            benefit_income / guideline,
            payment.poverty_ratio.minimum,
            payment.poverty_ratio.maximum,
        )
        heating_cost = spm_unit("wi_wheap_heating_cost", period)
        formula_amount = (
            (payment.benefit_ratio - poverty_ratio)
            / payment.funding_factor
            * heating_cost
        )
        amount = min_(np.floor(formula_amount), payment.maximum)
        # The February 1 reduction, supplemental benefits and the separate
        # non-heating electric benefit are not modeled.
        return where(amount >= payment.minimum, amount, 0)
