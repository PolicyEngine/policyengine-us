from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nj.njdhs.ccap.nj_ccap_time_category import (
    NJCCAPTimeCategory,
)


class nj_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "New Jersey CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/Copayment_Schedule.pdf#page=1",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=40",
        "https://www.nj.gov/humanservices/notices/documents/rules-and-regulations/NJAC%2010_15%20CHILD%20CARE%20SERVICES.PDF#page=85",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.copay
        countable_income = spm_unit("nj_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, countable_income / fpg, 0)

        person = spm_unit.members
        is_eligible_child = person("nj_ccap_eligible_child", period)
        time_category = person("nj_ccap_time_category", period)
        is_ft = time_category == NJCCAPTimeCategory.FULL_TIME
        # Copay scales with children actually receiving care, not merely
        # those who would be eligible. Follows the VA CCSP (va_ccsp_copay)
        # and SC CCAP (sc_ccap_copay) pattern of gating the child count on
        # an "in care" flag.
        # Reported care days or hours establish participation independently
        # of the missing-hours pricing fallback.
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        daily_hours = person("childcare_hours_per_day", period.this_year)
        monthly_days = person("childcare_attending_days_per_month", period.this_year)
        weekly_days = person("childcare_days_per_week", period.this_year)
        in_care = (
            (weekly_hours > 0)
            | (daily_hours > 0)
            | (monthly_days > 0)
            | (weekly_days > 0)
        )
        is_paying_child = is_eligible_child & in_care
        referred = person("nj_ccap_has_cpp_referral", period) & is_eligible_child
        protective = referred | person("receives_or_needs_protective_services", period)
        # 10:15-9.1(e)-(g): CP&P-paid foster placements are exempt. In-home
        # protective care requires a case-specific waiver; an exempt child's
        # status does not waive the copay for other children in the family.
        exempt_child = protective & (
            person("is_in_foster_care", period)
            | person("nj_ccap_cpp_copay_waived", period)
        )
        ordinary_requirements = spm_unit("nj_ccap_income_eligible", period) & spm_unit(
            "nj_ccap_activity_eligible", period
        )
        payable_child = referred | spm_unit.project(ordinary_requirements)
        is_paying_child = (
            is_paying_child
            & ~exempt_child
            & where(spm_unit.project(spm_unit.any(referred)), payable_child, True)
        )

        n_paying = spm_unit.sum(is_paying_child)
        n_ft = spm_unit.sum(is_paying_child & is_ft)
        has_second_child = n_paying >= 2

        # First child rate: use FT rate if any child is FT, else PT
        first_child_rate = where(
            n_ft > 0,
            p.first_child_ft_rate.calc(fpl_ratio),
            p.first_child_pt_rate.calc(fpl_ratio),
        )

        # Second child rate: FT only if 2+ FT children, otherwise PT
        second_child_rate = where(
            n_ft >= 2,
            p.second_child_ft_rate.calc(fpl_ratio),
            p.second_child_pt_rate.calc(fpl_ratio),
        )

        total_rate = first_child_rate + where(has_second_child, second_child_rate, 0)
        return where(n_paying == 0, 0, countable_income * total_rate)
