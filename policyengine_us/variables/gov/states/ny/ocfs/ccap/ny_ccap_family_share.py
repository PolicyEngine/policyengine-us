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
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap
        income = spm_unit("ny_ccap_countable_income", period)
        # 18 NYCRR 415.1(k) defines the state income standard as the most
        # recent federal income official poverty line, so spm_unit_fpg is the
        # standard itself rather than a proxy for it.
        state_income_standard = spm_unit("spm_unit_fpg", period)
        # 415.3(e)(3) applies the rate to income above the standard, so a
        # family at or below it has a zero income-based share, and the
        # 415.3(e)(4) minimum reaches only a family "required to pay an
        # income-based portion of a family share". The categorical exceptions
        # in 415.3(e)(1) are applied through ny_ccap_family_share_exempt.
        calculated_share = (income - state_income_standard) * p.family_share_rate
        minimum_share = p.minimum_weekly_family_share * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        income_based_share = where(
            income > state_income_standard,
            max_(calculated_share, minimum_share),
            0,
        )
        exempt = spm_unit("ny_ccap_family_share_exempt", period)
        return where(exempt, 0, income_based_share)
