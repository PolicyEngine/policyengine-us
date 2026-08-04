from policyengine_us.model_api import *


class ca_sbd_general_relief_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "San Bernardino County General Relief assistance unit size"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = "https://sanbernardino.legistar1.com/sanbernardino/attachments/eae80072-cef4-49e5-b04e-a9b442290034.docx"

    # The grant level is based on the number of eligible persons: members
    # barred for SSI/SSP, CAPI, or CalWORKs receipt, immigration status,
    # treatment-facility residence, or lack of linkage are not counted.
    # A member barred for other-assistance receipt also has their income
    # excluded from AU income; members excluded for other reasons remain
    # family members whose income still counts.
    adds = ["ca_sbd_general_relief_eligible_person"]
