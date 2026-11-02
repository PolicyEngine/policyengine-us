from policyengine_us.model_api import *


class sc_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "South Carolina LIHEAP eligible household size"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/WAP%202026%20State%20Plan.pdf#page=23",
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20South%20Carolina%20LIHEAP%20Model%20Plan%20w%20Attachments.pdf#page=529",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # This agency plan expressly attributes the size exclusion, while
        # retaining all members' income, to South Carolina LIHEAP guidance.
        qualified = person("is_citizen_or_legal_immigrant", period)
        # OEO's 2024 guide leaves state-placed foster children out of the household.
        # The input reads "qualifying foster care institution", the closest available.
        foster = person("is_in_foster_care", period.first_month)
        return spm_unit.sum(qualified & ~foster)
