from policyengine_us.model_api import *


class ky_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kentucky CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=10",
        "https://www.chfs.ky.gov/agencies/dcbs/dcc/Documents/dcc11319.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        # 922 KAR 2:160 Section 9(5) (citing 42 U.S.C. 9858c(c)(2)(N)) and the
        # DCC-113 fact sheet (effective Oct 1, 2023): gross monthly income must be
        # at or below 85% of the Kentucky state median income by family size.
        # Section 8(3): a child eligible under the Protection and Permanency
        # pathway (Section 5) is eligible without regard to the family's income.
        # We proxy P&P status with a child in foster care receiving protective
        # services.
        p = parameters(period).gov.states.ky.dcbs.ccap.income.smi_limit
        countable_income = spm_unit("ky_ccap_countable_income", period)
        family_size = spm_unit("spm_unit_size", period.this_year)
        # The DCC-113 table lists limits for family sizes 2-8; for larger families
        # add the per-additional-person amount for each member over eight. A
        # CCAP family always includes at least one adult and one child, so the
        # table's smallest size (2) is used as the floor for the lookup.
        capped_size = np.clip(family_size, 2, 8).astype(int)
        base_limit = p.main[capped_size]
        extra_members = max_(family_size - 8, 0)
        income_limit = base_limit + extra_members * p.additional
        is_tanf = spm_unit("is_tanf_enrolled", period)
        is_protection_permanency = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return is_tanf | is_protection_permanency | (countable_income <= income_limit)
