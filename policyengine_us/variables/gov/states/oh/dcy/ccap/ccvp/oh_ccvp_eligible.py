from policyengine_us.model_api import *


class oh_ccvp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Ohio Child Care Choice Voucher Program"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        # PDF pages 3-4
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_36.pdf#page=3",
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners%20and%20Providers/Rules%20and%20Resources/2026/PL_45.pdf#page=2",
        "https://www.lsc.ohio.gov/assets/legislation/136/hb96/en0/files/hb96-kid-bill-analysis-as-enacted-136th-general-assembly.pdf#page=10",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.dcy.ccap.ccvp
        if not p.in_effect:
            return np.zeros_like(
                spm_unit("spm_unit_size", period.this_year), dtype=bool
            )
        has_eligible_child = add(spm_unit, period, ["oh_ccvp_eligible_child"]) > 0
        # H.B. 96, Section 423.190: the family fails the income conditions for
        # Publicly Funded Child Care and income does not exceed 200% of the
        # poverty line. Procedure Letters 21 and 45 print this limit rounded up
        # to the next whole dollar, as they print the other limits.
        # Round to cents first so floating-point noise can't push an exact
        # dollar up.
        income_limit = np.ceil(
            np.round(spm_unit("oh_ccap_fpg", period) * p.fpl_rate, 2)
        )
        within_limit = spm_unit("oh_ccap_countable_income", period) <= income_limit
        fails_pfcc_income_test = ~spm_unit("oh_ccap_income_eligible", period)
        # Procedure Letter 36: families meet every other Publicly Funded Child
        # Care requirement.
        activity_eligible = spm_unit("oh_ccap_activity_eligible", period)
        asset_limit = parameters(period).gov.hhs.ccdf.asset_limit
        asset_eligible = (
            add(spm_unit, period.this_year, ["bank_account_assets"]) <= asset_limit
        )
        # Procedure Letter 36: families eligible for Publicly Funded Child Care
        # cannot use the voucher. Protective care and homeless families qualify
        # for that program without its income test.
        pfcc_eligible = spm_unit("oh_ccap_eligible", period)
        return (
            has_eligible_child
            & within_limit
            & fails_pfcc_income_test
            & activity_eligible
            & asset_eligible
            & ~pfcc_eligible
        )
