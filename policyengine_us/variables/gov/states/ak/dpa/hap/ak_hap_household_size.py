from policyengine_us.model_api import *


class ak_hap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Alaska HAP household size"
    reference = "http://dpaweb.hss.state.ak.us/manuals/HAP/3002/3002-1_households.htm"
    defined_for = StateCode.AK

    # The SPM unit approximates the economic household sharing heating costs.
    # Citizenship/status inputs lack finer qualified categories, COFA status,
    # documentation and SSN rules. No five-year waiting rule is applied.
    # Custody, foster arrangements and separate room-renter households are
    # not fully observed. Excluded members' otherwise countable income remains.
    adds = ["is_citizen_or_legal_immigrant"]
