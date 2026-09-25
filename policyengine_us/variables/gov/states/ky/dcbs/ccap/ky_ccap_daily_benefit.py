from policyengine_us.model_api import *


class ky_ccap_daily_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Kentucky CCAP daily benefit per child"
    definition_period = MONTH
    defined_for = "ky_ccap_eligible_child"
    reference = (
        "https://apps.legislature.ky.gov/law/kar/downloads/docs/10239/document.engrossed.pdf#page=10",
        "https://apps.legislature.ky.gov/law/kar/registers/49Ky_R_2022-23/02_Aug.pdf#page=70",
        "https://www.chfs.ky.gov/agencies/dcbs/dcc/Documents/dcc300kymaxpaymentchart.pdf#page=1",
    )

    def formula(person, period, parameters):
        # 922 KAR 2:160 Section 10(1)-(4): the per-child daily maximum is the
        # DCC-300 rate plus any rate supplements, capped at the provider's charge
        # to the general public (Section 10(4)).
        p = parameters(period).gov.states.ky.dcbs.ccap
        daily_rate = person("ky_ccap_daily_rate", period)
        # Section 10(3) special-care rate: a daily supplement for a child with
        # a special need. We approximate special-need status with is_disabled
        # and has_developmental_delay.
        has_special_need = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        under_court_supervision = person("is_under_court_supervision", period.this_year)
        age = person("age", period.this_year)
        # Section 10(3)(b) also covers court-supervised children age 13 but
        # under 19, the same band the Section 3(1)(b) eligibility age
        # parameters set, so those parameters are reused here.
        court_special_care = (
            under_court_supervision
            & (age >= p.eligibility.child_age_limit)
            & (age < p.eligibility.special_needs_child_age_limit)
        )
        special_care_supplement = where(
            has_special_need | court_special_care, p.supplements.special_care, 0
        )
        # We don't track provider accreditation (Section 10(2)(a)) or
        # nontraditional-hours care (Section 10(2)(b)) at the moment, so those
        # rate supplements are not applied.
        total_rate = daily_rate + special_care_supplement
        # Section 10(4): reimbursement is capped at the amount the provider
        # charges the general public.
        pre_subsidy = person("pre_subsidy_childcare_expenses", period)
        monthly_care_days = person(
            "childcare_attending_days_per_month", period.this_year
        )
        mask = monthly_care_days > 0
        daily_charge = np.divide(
            pre_subsidy,
            monthly_care_days,
            out=np.zeros_like(pre_subsidy, dtype=float),
            where=mask,
        )
        return max_(min_(total_rate, daily_charge), 0)
