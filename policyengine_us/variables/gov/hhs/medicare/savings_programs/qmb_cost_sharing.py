from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.savings_programs.category.msp_category import (
    MSPCategory,
)


class qmb_cost_sharing(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Qualified Medicare Beneficiary cost-sharing value"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396d#p_3",
    )
    documentation = (
        "First-pass monthly value of QMB coverage for Medicare deductibles, "
        "coinsurance, and copayments. The model lacks beneficiary-level "
        "Medicare claims, so this approximates cost sharing as a parameterized "
        "share of average Medicare per-capita spending."
    )

    def formula(person, period, parameters):
        category = person("msp_category", period)
        p = parameters(period).gov.hhs.medicare.savings_programs
        monthly_medicare_cost = (
            parameters(period).calibration.gov.hhs.medicare.per_capita_cost
            / MONTHS_IN_YEAR
        )
        return (
            (category == MSPCategory.QMB)
            * monthly_medicare_cost
            * p.qmb.cost_sharing_rate
        )
