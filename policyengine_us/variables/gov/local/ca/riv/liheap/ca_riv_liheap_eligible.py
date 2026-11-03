from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ca_riv_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the California Riverside County LIHEAP"
    definition_period = YEAR
    defined_for = "in_riv"
    reference = (
        "https://capriverside.org/utility-assistance-program",
        # 2025 HEAP and Fast Track payment table (PDF page 180).
        "https://www.csd.ca.gov/Shared%20Documents/2025-Final-LIHEAP-State-Plan.pdf#page=180",
        # 2026 HEAP and Fast Track payment table (PDF page 184).
        "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=184",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        p_riv = parameters(period).gov.local.ca.riv.cap.liheap
        state_median_income = spm_unit("hhs_smi", period)
        # The income concept is not clearly defined, assuming IRS gross income
        countable_income = spm_unit("ca_riv_liheap_countable_income", period)
        smi_limit = state_median_income * p.smi_limit
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. California's printed CSD tables fall below
        # that floor at sizes 20 to 25 in 2025 and 21 to 25 in 2026, and the
        # modeled 60% SMI limit does so from size 20 in 2025 and size 21 in
        # 2026 and 2027.
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            size, state_group, period, parameters, year_lag=p_riv.fpg_year_lag
        )
        floor = np.round(guideline * p.fpg_floor, 2)
        return (countable_income <= smi_limit) | (countable_income < floor)
