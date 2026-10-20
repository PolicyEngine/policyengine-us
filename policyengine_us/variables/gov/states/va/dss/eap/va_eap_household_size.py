from policyengine_us.model_api import *


class va_eap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Virginia EAP household size"
    documentation = "Number of household members who are U.S. citizens or qualified aliens. Other members are not counted in household size, although their income counts toward household income. The Social Security number requirement for adult members has no input and is not modeled."
    reference = (
        # PDF pages 31-32, 41
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=31",
        "https://law.lis.virginia.gov/admincodefull/title22/agency40/chapter680/",
    )
    defined_for = StateCode.VA

    # Manual B.7: "An individual is not counted in the Energy Assistance
    # household size, if he/she does not meet either of these criteria
    # [citizen or qualified alien]. However, his/her income is counted in the
    # Energy Assistance household's total income."
    adds = ["is_citizen_or_legal_immigrant"]
