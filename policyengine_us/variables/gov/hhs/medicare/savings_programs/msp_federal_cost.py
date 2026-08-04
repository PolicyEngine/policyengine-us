from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.savings_programs.category.msp_category import (
    MSPCategory,
)


class msp_federal_cost(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program federal cost"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396b",
        "https://www.law.cornell.edu/uscode/text/42/1396d#b",
        "https://www.law.cornell.edu/uscode/text/42/1396u-3#d",
    )
    documentation = (
        "Federal share of limited-benefit Medicare Savings Program cost. "
        "QMB and SLMB use the state's regular FMAP; QI uses the 100% federal "
        "share within the state allocation."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs
        state = person.household("state_code", period)
        regular_fmap = p.medicaid.cost_share.fmap[state]

        federal_cost = 0
        for month in period.get_subperiods(MONTH):
            category = person("msp_category", month)
            monthly_cost = person("msp_benefit_value", month) + person(
                "qmb_cost_sharing", month
            )
            federal_share = select(
                [
                    category == MSPCategory.QMB,
                    category == MSPCategory.SLMB,
                    category == MSPCategory.QI,
                ],
                [
                    regular_fmap,
                    regular_fmap,
                    p.medicare.savings_programs.qi.federal_share,
                ],
                default=0,
            )
            federal_cost += monthly_cost * federal_share

        return where(person("medicaid_enrolled", period), 0, federal_cost)
