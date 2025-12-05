from policyengine_us.model_api import *


class has_bcc_qualifying_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Has health coverage that qualifies for breast/cervical cancer treatment"
    definition_period = YEAR
    reference = "https://www.dhs.state.il.us/page.aspx?item=33528"

    def formula(person, period, parameters):
        # Per PM 06-20-02, a person is considered "uninsured" for BCC purposes
        # unless they have coverage that would pay for cancer treatment.
        # Exceptions (still considered uninsured):
        # - Coverage with limited benefits
        # - Coverage where lifetime cap has been met/exceeded
        # - Coverage that excludes cancer treatment
        # - Indian Health Service coverage only
        #
        # This variable returns True if the person has creditable coverage
        # that would disqualify them from BCC. It defaults to assuming ESI
        # provides adequate coverage, but can be overridden by the user.
        has_esi = person("has_esi", period)
        # Assume marketplace coverage also provides creditable coverage
        has_marketplace = person("has_marketplace_health_coverage", period)
        return has_esi | has_marketplace
