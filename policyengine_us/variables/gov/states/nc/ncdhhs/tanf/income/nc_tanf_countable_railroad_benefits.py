from policyengine_us.model_api import *


class nc_tanf_countable_railroad_benefits(Variable):
    value_type = float
    entity = Person
    label = "North Carolina Work First countable railroad retirement benefits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/wf-114_1-2-2024.pdf#page=2"
    )

    def formula(person, period, parameters):
        gross = person("railroad_benefits", period)
        withheld = person("railroad_benefits_medicare_premium_withheld", period)
        return max_(gross - withheld, 0)
