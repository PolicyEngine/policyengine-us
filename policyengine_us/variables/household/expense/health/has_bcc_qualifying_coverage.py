from policyengine_us.model_api import *


class has_bcc_qualifying_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Has health coverage that qualifies for breast/cervical cancer treatment"
    definition_period = YEAR
    reference = "https://www.dhs.state.il.us/page.aspx?item=33528"
    # Per PM 06-20-02, a person is considered "uninsured" for BCC purposes
    # unless they have coverage that would pay for cancer treatment.
    # The following do NOT count as qualifying coverage:
    # - Coverage with limited benefits
    # - Coverage where lifetime cap has been met/exceeded
    # - Coverage that excludes cancer treatment
    # - Indian Health Service coverage only
