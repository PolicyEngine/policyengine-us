from policyengine_us.model_api import *


class wi_ssi_e_for_home_care(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin SSI-E pays for care in the assisted home"
    definition_period = MONTH
    reference = (
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2023-27pihn.pdf#page=81",
        "https://www.dhs.wisconsin.gov/publications/p20679-26-01.pdf#page=13",
    )
    # The certified SSI-E payment funds care enabling this disabled person to remain in
    # the family's assisted natural home. False for a substitute-care or facility award,
    # or care for someone outside the assisted family. Certification alone does not
    # establish this purpose. Identify the co-resident family caregiver with
    # wi_ssi_e_caregiver_id.
