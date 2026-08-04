from policyengine_us.model_api import *


class ca_sbd_general_relief_real_property_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "San Bernardino County General Relief real property value"
    defined_for = "in_sbd"
    reference = "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx"

    # Combined assessed value of real property; no encumbrances are
    # deducted. The county's rule evaluating a vehicle used as the
    # principal residence under this limit is not modeled — vehicles are
    # always evaluated under the personal property test.
    adds = ["assessed_property_value"]
