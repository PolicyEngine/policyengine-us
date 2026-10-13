from policyengine_us.model_api import *


class wi_ssp(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin State SSI Supplement"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.WI
    reference = (
        "https://www.emhandbooks.wisconsin.gov/ssi-admin/2/2.1_federal_and_state_ssi_recipients.htm",
        "https://www.dhs.wisconsin.gov/dms/memos/ops/dms-ops-2026-12.pdf#page=2",
    )
    adds = ["wi_ssp_regular", "wi_ssi_e", "wi_cts"]
