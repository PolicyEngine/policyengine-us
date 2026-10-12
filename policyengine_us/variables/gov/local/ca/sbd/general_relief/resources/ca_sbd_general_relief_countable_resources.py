from policyengine_us.model_api import *


class ca_sbd_general_relief_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "San Bernardino County General Relief countable resources"
    defined_for = "in_sbd"
    reference = "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx"

    # Total non-exempt personal property counted toward the $500 limit:
    # liquid assets, other personal property, and the non-exempt portion of
    # vehicle value. Cemetery plots, tools of the trade, and insurance cash
    # surrender values have no model inputs and are not tracked.
    adds = [
        "spm_unit_cash_assets",
        "personal_property",
        "ca_sbd_general_relief_countable_vehicle_value",
    ]
