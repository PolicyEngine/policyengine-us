from policyengine_us.model_api import *


class oh_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-03"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.dcy.ccap.income
        sources = add(spm_unit, period, p.countable_income.sources)
        person = spm_unit.members
        # 5180:2-16-03(D)(1) counts self-employment as the total profit from
        # a business enterprise and (D)(4)(a) disallows net losses, so each
        # member's loss from a signed net-flow source is added back rather
        # than offsetting other income.
        loss_amounts = [
            min_(person(source, period), 0)
            for source in p.countable_income.net_loss_sources
        ]
        losses = sum(loss_amounts)
        receives_ssi = person("ssi", period) > 0
        is_excluded_minor_student = (
            (person("age", period.this_year) < p.countable_income.minor_age_limit)
            & person("is_full_time_student", period.this_year)
            & ~person("is_parent", period.this_year)
        )
        # The excluded earned income matches the floored amounts counted
        # above, so a loss source contributes zero here as well.
        earned_loss_amounts = [
            min_(person(source, period), 0)
            for source in p.countable_income.earned_sources
            if source in p.countable_income.net_loss_sources
        ]
        person_earned_income = add(
            person, period, p.countable_income.earned_sources
        ) - sum(earned_loss_amounts)
        excluded_earned_income = spm_unit.sum(
            person_earned_income * (receives_ssi | is_excluded_minor_student)
        )
        return sources - spm_unit.sum(losses) - excluded_earned_income
