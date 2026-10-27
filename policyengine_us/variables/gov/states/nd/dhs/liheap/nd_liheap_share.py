from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit, smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nd_liheap_share(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "North Dakota LIHEAP heating expense share"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ND_BenefitMatrix_2026.xlsx",
        "https://www.nd.gov/dhs/policymanuals/415/415_30_10.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_30_05.htm",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        "https://www.law.cornell.edu/uscode/text/42/8622",
        # PDF pages 2, 5
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=2",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.liheap
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("nd_liheap_household_size", period)
        income = spm_unit("nd_liheap_countable_income", period)
        # The published dollar bands differ from the federal SMI formula.
        # Clip only the table lookup; larger households use their actual size.
        table_size = clip(size, 1, p.maximum_published_size)
        published_limits = p.income_limits[table_size]
        state = spm_unit.household("state_code_str", period)
        state_median_income = smi(size, state, period, parameters)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # 42 U.S.C. 8624(b)(2)(B) pays only households with income not above
        # the greater of 150% of the poverty guideline and 60% of the state
        # median income, which 8622(11) defines as HHS's size-adjusted figure.
        # HHS LIHEAP IM 2025-02 Attachment 4 (pages 2 and 5) prints North
        # Dakota's FY2026 60% amounts, which liheap_smi_limit reproduces. The
        # FY2026 table's 60% column exceeds them by $2 to $12 at sizes 2-9, 11
        # and 12, where 60% of SMI is the greater amount, so no band extends
        # above this federal maximum.
        federal_maximum = max_(
            liheap_smi_limit(size, state, p_hhs.smi_limit, period, parameters),
            guideline * p_hhs.fpg_limit,
        )
        # Beyond the published table, statutory SMI percentages are an
        # approximation with unverified state rounding, not a size exclusion.
        limits = [
            min_(
                where(
                    size <= p.maximum_published_size,
                    published_limits[str(index)],
                    state_median_income * rate,
                ),
                federal_maximum,
            )
            for index, rate in enumerate(p.smi_band_limits, start=1)
        ]
        share = select(
            [income <= limit for limit in limits],
            p.shares,
            default=0,
        )
        federal_floor = np.round(guideline * p_hhs.fpg_floor, 2)
        # Federal protection gives an otherwise excluded household the minimum share.
        share = where((share == 0) & (income < federal_floor), p.shares[-1], share)
        return where(size > 0, share, 0)
