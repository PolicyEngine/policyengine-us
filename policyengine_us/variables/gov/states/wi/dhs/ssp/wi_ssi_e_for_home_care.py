from policyengine_us.model_api import *


class wi_ssi_e_for_home_care(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin SSI-E pays for family-member care in the assisted home"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/24/5.609",
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2023-27pihn.pdf#page=81",
        "https://www.dhs.wisconsin.gov/publications/p20679-26-01.pdf#page=13",
    )
    # The certified SSI-E payment funds care, provided by a member of the assisted
    # family, that enables this disabled person to remain in the family's assisted
    # unit (24 CFR 5.609(b)(19)). False for a substitute-care or facility award, care
    # by someone outside the assisted family, or certification alone.
