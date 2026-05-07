from policyengine_us.model_api import *


class de_tanf_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "Delaware TANF countable earned income per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/detanfstateplan2017.pdf#page=6",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # Per DSSM 4008 / State Plan Exhibit 1 Step 3:
        # For benefit calculation, subtract from each earner's income:
        # 1. $90 standard work expense
        # 2. $30 flat disregard
        # 3. 1/3 of remainder
        #
        # NOTE: The $30+1/3 disregard is limited to 4 consecutive months,
        # followed by $30 only for 8 months, then neither until 12 months
        # without TANF. We always apply the full $30+1/3 disregard.
        # See: https://help.workworldapp.com/wwwebhelp/de_earned_income_disregards_tanf_and_ga.htm
        p = parameters(period).gov.states.de.dhss.tanf.income

        gross_earned = person("tanf_gross_earned_income", period)
        has_earnings = gross_earned > 0

        # Step 1: Subtract $90 work expense per earner
        after_work_expense = max_(
            gross_earned - p.deductions.work_expense * has_earnings, 0
        )

        # Step 2: Subtract $30 flat disregard per earner
        after_thirty = max_(
            after_work_expense
            - p.deductions.earned_income_disregard.flat * has_earnings,
            0,
        )

        # Step 3: Subtract 1/3 of remainder
        one_third_disregard = (
            after_thirty * p.deductions.earned_income_disregard.percentage
        )
        return max_(after_thirty - one_third_disregard, 0)
