from policyengine_us.model_api import *


class md_total_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD total personal exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-211&enactments=false"

    def formula(tax_unit, period, parameters):
        # § 10-211(b)(1): the per-exemption amount for each exemption allowed
        # under § 10-211(a).
        md_personal_exemption = tax_unit("md_personal_exemption", period)
        exemptions = tax_unit("md_personal_exemptions_count", period)
        return md_personal_exemption * exemptions
