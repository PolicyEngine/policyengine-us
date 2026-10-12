from policyengine_us.model_api import *


class wi_ssi_e_caregiver_id(Variable):
    value_type = int
    entity = Person
    label = "Person ID of the Wisconsin SSI-E home caregiver"
    definition_period = YEAR
    quantity_type = STOCK
    default_value = 0
    reference = (
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2023-27pihn.pdf#page=81"
    )
    # Nonzero person_id of the family member providing the qualifying home care. Zero
    # means unknown. The caregiver must be a different person in the same household and
    # assisted SPM unit (the HUD family). Use distinct person IDs within the household.
    # This annual identifier is read without division in monthly calculations, like
    # parent IDs. Within-year changes of caregiver require separate scenarios.
