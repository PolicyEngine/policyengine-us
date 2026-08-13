from policyengine_us.model_api import *


class or_erdc_monthly_care_hours(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = "hour"
    label = "Oregon ERDC monthly child care hours"
    defined_for = "or_erdc_eligible_child"
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0023",
        "https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/de2818.pdf#page=428",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].delc.erdc.hours
        need_hours = person.spm_unit("or_erdc_caretaker_weekly_need_hours", period)
        # OAR 414-175-0023(5)(a): band the weekly need into 20 / 40 / up to 75
        # allowed weekly hours.
        banded_weekly = p.authorized.weekly.calc(need_hours)
        # OAR 414-175-0023(5)(b): categorically eligible caretakers receive a
        # 20-hour weekly baseline even when the activity test is waived.
        categorical = person.spm_unit("or_erdc_categorically_eligible", period)
        weekly_allowance = where(
            categorical,
            max_(banded_weekly, p.authorized.categorical_default),
            banded_weekly,
        )
        # OAR 414-175-0023(5)(c)-(d): add a travel allowance, then convert the
        # weekly allowance to monthly hours, capped at the monthly maximum.
        weekly_with_travel = weekly_allowance * (1 + p.authorized.travel_allowance)
        monthly = weekly_with_travel * p.authorized.weekly_to_monthly
        # The OPEN worker guide (p. 428) publishes the 20-hour band as 108
        # monthly hours (20 * 1.25 * 4.3 = 107.5), so fractional monthly
        # hours round up before the cap. OAR 414-175-0075(9)-(10) allow
        # payment beyond the cap (up to about 323 hours) with a
        # Department-approved special-circumstances determination, which is
        # not modeled (see hours/max_monthly.yaml).
        return min_(np.ceil(monthly), p.max_monthly)
