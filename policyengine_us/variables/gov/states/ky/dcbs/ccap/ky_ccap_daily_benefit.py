from policyengine_us.model_api import *


class ky_ccap_daily_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Kentucky CCAP daily benefit per child"
    definition_period = MONTH
    defined_for = "ky_ccap_eligible_child"
    reference = (
        "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=10",
        "https://www.chfs.ky.gov/agencies/dcbs/dcc/Documents/dcc300kymaxpaymentchart.pdf#page=1",
    )

    def formula(person, period, parameters):
        # 922 KAR 2:160 Section 10(1)-(4): the per-child daily maximum is the
        # DCC-300 rate plus any rate supplements, capped at the provider's charge
        # to the general public (Section 10(4)).
        p = parameters(period).gov.states.ky.dcbs.ccap
        daily_rate = person("ky_ccap_daily_rate", period)
        # Section 10(3) special-care rate: +$1/day for a child with a special
        # need. We approximate special-need status with is_disabled and
        # has_developmental_delay.
        has_special_need = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        special_care_supplement = where(has_special_need, p.supplements.special_care, 0)
        # We don't track provider accreditation (Section 10(2)(a), +$2/day) or
        # nontraditional-hours care (Section 10(2)(b), +$1/day) at the moment, so
        # those rate supplements are not applied.
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
