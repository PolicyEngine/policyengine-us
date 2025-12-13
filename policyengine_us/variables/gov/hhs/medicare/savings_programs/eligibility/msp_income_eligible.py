from policyengine_us.model_api import *


class msp_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program income eligible"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/cfr/text/42/435.121",
    )

    def formula(person, period, parameters):
        # Income eligible if under the QI threshold (135% FPL)
        # which is the highest threshold for standard MSP levels
        p = parameters(
            period
        ).gov.hhs.medicare.savings_programs.eligibility.income.qi
        fpg = person("msp_fpg", period)
        countable_income = person("msp_countable_income", period)

        # Use QI threshold (135% FPL) as the outer bound
        qi_income_limit = fpg * p.fpl_limit

        return countable_income <= qi_income_limit
