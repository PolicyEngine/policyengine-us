from policyengine_us.model_api import *


class medicare_gross_cost(Variable):
    value_type = float
    entity = Person
    label = "Gross Medicare cost"
    documentation = (
        "Annual Medicare spending on behalf of the beneficiary before "
        "subtracting beneficiary premiums: CMS Medicare spending per "
        "enrollee, which covers Parts A through D, including the Part D "
        "low-income subsidy. CBO's standard household income counts "
        "Medicare net of premiums instead (cbo_medicare_benefit); CBO adds "
        "the premiums back only in an expanded sensitivity measure, which "
        "it calls gross Medicare spending."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.cms.gov/about-cms/what-we-do/medicare",
        "https://www.cbo.gov/publication/61910",
    )
    defined_for = "medicare_enrolled"

    def formula(person, period, parameters):
        return parameters(period).calibration.gov.hhs.medicare.per_capita_cost
