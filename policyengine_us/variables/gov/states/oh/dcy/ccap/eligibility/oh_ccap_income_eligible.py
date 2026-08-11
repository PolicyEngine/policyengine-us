from policyengine_us.model_api import *


class oh_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Ohio CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_21.pdf#page=2",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-03",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-02",
    )

    def formula(spm_unit, period, parameters):
        # DCY Procedure Letter 21: initial (intake) eligibility caps family
        # income at 145% of the federal poverty guideline; once enrolled, a
        # family remains eligible until income exceeds 300% FPG. A family with
        # a special-needs child uses a 150% FPG initial limit, as does a
        # family in the post-Ohio Works First transitional period
        # (5180:6-1-02(F)).
        p = parameters(period).gov.states.oh.dcy.ccap.income.fpl_rate
        countable_income = spm_unit("oh_ccap_countable_income", period)
        # oh_ccap_fpg is the October-vintage monthly FPG per PL 21.
        fpg = spm_unit("oh_ccap_fpg", period)
        person = spm_unit.members
        special_needs_child = person("oh_ccap_eligible_child", period) & person(
            "oh_ccap_special_needs", period
        )
        has_special_needs_child = spm_unit.sum(special_needs_child) > 0
        # A special-needs child raises the initial limit to 150% FPG.
        base_initial_rate = where(
            has_special_needs_child,
            p.special_needs_eligibility,
            p.initial_eligibility,
        )
        # 5180:6-1-02(F)(1)(a): transitional child care requires employment;
        # full-time study alone does not qualify the former OWF caretaker.
        transitional_caretaker = person("oh_ccap_owf_transitional", period)
        employed = person("weekly_hours_worked", period.this_year) > 0
        transitional_qualifies = spm_unit.sum(transitional_caretaker & employed) > 0
        initial_rate = max_(
            base_initial_rate,
            transitional_qualifies * p.transitional_eligibility,
        )
        enrolled = spm_unit("oh_ccap_enrolled", period)
        rate = where(enrolled, p.ongoing_eligibility, initial_rate)
        # PL 21 publishes the monthly dollar standards rounded up to the next
        # whole dollar.
        income_limit = np.ceil(fpg * rate)
        return countable_income <= income_limit
