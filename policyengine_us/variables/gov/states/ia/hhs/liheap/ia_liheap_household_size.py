from policyengine_us.model_api import *


class ia_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP household size"
    documentation = (
        "Number of household members counted as application participants. "
        "Section 7.00 requires each member to verify United States citizenship, "
        "primarily by Social Security Number, 'to be counted towards the total "
        "size of the household'; Section 7.30 excludes a member without the "
        "required documents from the participant count while 'the ineligible "
        "member's income must be counted'. Iowa's test is documentary (SSN, "
        "I-94 or approved alternative documents); is_citizen_or_legal_immigrant "
        "approximates it. The SPM unit approximates the housing unit, so "
        "dual-household children, roomers, live-in caregivers, incarcerated "
        "members and students away from home are not identified."
    )
    reference = (
        # Sections 7.00 and 7.30; Definitions, Household/Customer.
        # PDF pages 31, 34, 82
        "https://hhs.iowa.gov/media/17262/download?inline#page=31",
    )
    defined_for = StateCode.IA

    adds = ["is_citizen_or_legal_immigrant"]
