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
        # P&P status covers a child in foster care or one receiving or needing
        # child protective or preventive services. The waiver applies unit-wide
        # because Section 5(1)(a) keys on residing with an applicant who
        # receives or needs the services — every child co-residing with that
        # applicant qualifies, not only the flagged child.
        # We don't track employment in a licensed child-care center or
        # certified family child-care home at the moment, so the Section 4(4)
        # child-care-worker full income exclusion (eff. 11-18-2024) is not
        # applied. The Section 4(5) working-foster-parent income exclusion is
        # effectively covered by the P&P bypass above. We also don't track
        # months since an income change, so the Section 9(6) six-month
        # transitional period after exceeding the income limit is not modeled.
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
        person = spm_unit.members
        is_protection_permanency = spm_unit.any(
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        return is_tanf | is_protection_permanency | (countable_income <= income_limit)
