from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_living_arrangement_amount import (
    ssi_living_arrangement_amount,
)


class uncapped_ssi_without_spousal_deeming(Variable):
    value_type = float
    entity = Person
    label = "Uncapped SSI without spousal deeming"
    unit = USD
    documentation = (
        "Individual federal benefit rate less only the person's own countable "
        "income, the amount SSI under spousal deeming cannot exceed (can be "
        "below zero)."
    )
    definition_period = MONTH
    defined_for = "is_ssi_eligible"
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(e)(2)",
    )

    def formula(person, period, parameters):
        # 416.1163(e)(2): 'the amount remaining after we subtract only your
        # own countable income from an individual's Federal benefit rate'.
        # The rate takes the same living-arrangement adjustments as the rate
        # under deeming.
        p = parameters(period).gov.ssa.ssi.amount
        amount = ssi_living_arrangement_amount(person, period, parameters, p.individual)
        # Countable income adds income deemed from an ineligible spouse to the
        # person's own countable income; remove it.
        own_countable_income = person("ssi_countable_income", period) - person(
            "ssi_income_deemed_from_ineligible_spouse", period
        )
        return amount - own_countable_income
