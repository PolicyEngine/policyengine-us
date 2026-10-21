from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class oh_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Ohio HEAP annual income limit"
    defined_for = StateCode.OH
    reference = (
        "https://irp.cdn-website.com/aa88b0b1/files/uploaded/2022-24%20ATTACHMENT%202022-2023%20EAP%20Guidelines%20%281%29.pdf#page=7",
        "https://clevelandohio.gov/sites/clevelandohio/files/aging/2024-2025_HEAP_application_B_W_1.pdf#page=1",
        "https://www.clevelandohio.gov/sites/clevelandohio/files/aging/Home%20repair%20Applications/2025-2026_HEAP_application_B_W.pdf#page=1",
        "https://www.lccaa.net/wp-content/uploads/2026/07/2026-2027-EAP-Application-7-2026.pdf#page=1",
        "https://occ.ohio.gov/sites/default/files/2026-08/OCC-Home-Energy-Assistance-Program-HEAP_0.pdf#page=1",
        # HHS 60% SMI tables, Ohio row for sizes 7-12 and footnotes.
        # PDF pages 5-6
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM%202024-02_Att4SMITable.pdf#page=5",
        # PDF pages 5-6
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=5",
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
        # FPG applies to all sizes in 2022-23, sizes 1-7 in 2024-25 and
        # 2026-27, and sizes 1-8 in 2025-26. Flooring reproduces the printed
        # whole-dollar limits; the 2022-23 cents do not change the outcome for
        # whole-dollar income.
        fpg_limit = np.floor(guideline * p.fpg_rate)
        # Larger units use 60% of SMI: the current federal fiscal year's SMI for
        # 2024-25 and 2025-26 and the prior year's for 2026-27 (smi_year_lag),
        # inferred from the federal cap and the Consumers' Counsel limits.
        smi_date = period.start.offset(-int(p.smi_year_lag), "year")
        # The HHS floor order reproduces every HHS FFY2025 and FFY2026 amount
        # and the Consumers' Counsel 2026-27 sizes 8, 11 and 12. Its sizes 9
        # and 10 ($96,946, $99,010) exceed even unrounded 60% of SMI
        # ($96,945.68, $99,008.35); the HHS $96,944 and $99,007 apply.
        smi_limit = liheap_smi_limit(size, state, p.smi_rate, smi_date, parameters)
        limit = where(size <= p.maximum_fpg_household_size, fpg_limit, smi_limit)
        return where(size > 0, limit, 0)
