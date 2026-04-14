from policyengine_us.model_api import *


class dc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF) countable resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dhs.dc.gov/service/temporary-cash-assistance-needy-families-tanf",
        "https://dhs.dc.gov/sites/default/files/dc/sites/dhs/service_content/attachments/DC%20TANF%20State%20Plan_Oct-2023.pdf#page=40",
    )

    def formula(spm_unit, period, parameters):
        return spm_unit("spm_unit_cash_assets", period.this_year)

    defined_for = StateCode.DC
