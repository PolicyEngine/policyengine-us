from policyengine_us.model_api import *


class is_qi_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Qualifying Individual (QI) eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.125",
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.law.cornell.edu/uscode/text/8/1613#a",
    )

    def formula(person, period, parameters):
        # QI requires income at least 120% FPL but below 135% FPL
        # QI is only available for people who don't qualify for other Medicaid
        p = parameters(period).gov.hhs.medicare.savings_programs.eligibility.income

        medicare_eligible = person("is_medicare_eligible", period.this_year)
        # QMB, SLMB and QI are federal Medicaid benefits, so the federal Medicaid
        # immigration test (42 U.S.C. 1396b(v), 8 U.S.C. 1611(a) and 1613(a))
        # applies. State-funded Medicaid coverage does not open them.
        immigration_eligible = person(
            "is_federal_medicaid_immigration_status_eligible", period.this_year
        )
        asset_eligible = person("msp_asset_eligible", period)

        fpg = person("msp_fpg", period)
        countable_income = person("msp_countable_income", period)

        slmb_income_limit = fpg * p.slmb.fpl_limit
        qi_income_limit = fpg * p.qi.fpl_limit

        income_at_or_above_slmb = countable_income >= slmb_income_limit
        income_below_qi = countable_income < qi_income_limit
        income_eligible = income_at_or_above_slmb & income_below_qi

        # QI excludes those eligible for other Medicaid coverage
        medicaid_eligible = person("is_medicaid_eligible", period.this_year)

        return (
            medicare_eligible
            & immigration_eligible
            & income_eligible
            & asset_eligible
            & ~medicaid_eligible
        )
