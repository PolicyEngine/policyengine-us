from policyengine_us.model_api import *


class ca_sbd_general_relief_maximum_basic_grant(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Bernardino County General Relief maximum basic grant"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/eae80072-cef4-49e5-b04e-a9b442290034.docx",
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/b2fb756f-da07-452e-bdba-e3c4eda464c5.doc",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief.payment
        size = spm_unit("ca_sbd_general_relief_assistance_unit_size", period)
        # The grant table tops out at assistance units of five or more.
        capped_size = clip(size, 1, p.max_unit_size)
        return p.maximum_basic_grant[capped_size]
