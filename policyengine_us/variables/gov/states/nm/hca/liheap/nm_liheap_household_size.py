from policyengine_us.model_api import *


class nm_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New Mexico LIHEAP household size"
    defined_for = StateCode.NM
    reference = (
        # 8.150.410.8, 8.150.410.13 and 8.150.410.15 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0410.html",
        # 8.150.520.10 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0520.html",
    )

    # Citizens and qualified noncitizens form the benefit group and the
    # household size for the income limit and income points. The income of
    # other members is prorated in nm_liheap_countable_income. SPM membership
    # approximates the LIHEAP household, is_citizen_or_legal_immigrant
    # approximates TANF-qualified noncitizen status, and Social Security
    # number enumeration has no input.
    adds = ["is_citizen_or_legal_immigrant"]
