from policyengine_us.model_api import *


class mo_sab_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Missouri SAB citizenship and immigrant status requirement"
    definition_period = YEAR
    # The blind-only scope keeps non-blind SNC cases from evaluating Medicaid
    # parameters that are unavailable in some historical years.
    defined_for = "is_blind"
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0405-000-00/0405-030-00/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/",
    )

    def formula(person, period, parameters):
        # SAB applies the MO HealthNet for Families citizenship and immigrant
        # status requirement (§ 0405.030.00, § 1805.020.00).
        return person("is_medicaid_immigration_status_eligible", period)
