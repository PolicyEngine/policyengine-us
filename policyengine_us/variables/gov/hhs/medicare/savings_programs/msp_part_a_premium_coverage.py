from policyengine_us.model_api import *


class msp_part_a_premium_coverage(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Part A premium amount covered by MSP"
    definition_period = YEAR
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
    )
    documentation = (
        "Annual Part A premium amount paid on the enrollee's behalf through "
        "Qualified Medicare Beneficiary coverage."
    )

    def formula(person, period, parameters):
        enrolled = person("medicare_enrolled", period)
        monthly_part_a_premium = person("base_part_a_premium", period) / MONTHS_IN_YEAR
        monthly_coverage = 0
        for month in period.get_subperiods(MONTH):
            qmb_eligible = person("is_qmb_eligible", month)
            monthly_coverage += where(
                enrolled & qmb_eligible,
                monthly_part_a_premium,
                0,
            )
        return monthly_coverage
