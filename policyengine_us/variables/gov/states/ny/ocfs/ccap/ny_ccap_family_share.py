from policyengine_us.model_api import *


class ny_ccap_family_share(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "New York CCAP monthly family share"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=19",
        "https://ocfs.ny.gov/main/policies/external/ocfs_2021/ADM/21-OCFS-ADM-14.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        income = spm_unit("ny_ccap_countable_income", period)
        # 18 NYCRR 415.1(k) defines the state income standard as the most
        # recent federal income official poverty line, so spm_unit_fpg is the
        # standard itself rather than a proxy for it.
        state_income_standard = spm_unit("spm_unit_fpg", period)
        income_exceeding_standard = max_(income - state_income_standard, 0)
        p = parameters(period).gov.states.ny.ocfs.ccap
        # The rate is the district-elected ceiling of 10% under Social
        # Services Law 410-x(6) until the October 2023 revisions replaced it
        # with a statewide 1%; both eras are dated values of one parameter.
        calculated_share = income_exceeding_standard * p.family_share_rate
        minimum_share = p.minimum_weekly_family_share * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        # 415.3(e)(1) exempts families with income at or below 100 percent of
        # the state income standard from any family share; the $1 weekly
        # minimum under 415.3(e)(4) applies only to families paying an
        # income-based share. The categorical exceptions in the same
        # subdivision are applied through ny_ccap_family_share_exempt.
        income_based_share = where(
            income > state_income_standard,
            max_(calculated_share, minimum_share),
            0,
        )
        exempt = spm_unit("ny_ccap_family_share_exempt", period)
        return where(exempt, 0, income_based_share)
