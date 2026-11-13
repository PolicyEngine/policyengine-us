from policyengine_us.model_api import *


class is_slmb_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Specified Low-Income Medicare Beneficiary (SLMB) eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.124",
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.law.cornell.edu/uscode/text/8/1613#a",
    )

    def formula(person, period, parameters):
        # SLMB requires income above 100% FPL but below 120% FPL
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

        qmb_income_limit = fpg * p.qmb.fpl_limit
        slmb_income_limit = fpg * p.slmb.fpl_limit

        income_above_qmb = countable_income > qmb_income_limit
        income_below_slmb = countable_income < slmb_income_limit
        income_eligible = income_above_qmb & income_below_slmb

        return (
            medicare_eligible & immigration_eligible & income_eligible & asset_eligible
        )
