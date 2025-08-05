from policyengine_us.model_api import *


class ca_ala_general_assistance_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Alameda County General Assistance based on asset requirements"
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.local.ca.ala.general_assistance.asset.limit
        assets = spm_unit("spm_unit_cash_assets", period)
        return assets <= p.limit
