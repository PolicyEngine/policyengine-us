from policyengine_us.model_api import *


class md_total_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD total personal exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-211&enactments=false",
        # PDF pages 12-13: filing status 6 and Instruction 8.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
    )

    def formula(tax_unit, period, parameters):
        # § 10-211(a) and (b)(1) allow an exemption for each filer and for each
        # dependent "as defined in § 152 of the Internal Revenue Code". A
        # person who can be claimed on another return is a dependent taxpayer
        # (filing status 6): "You do not get an exemption for yourself". Under
        # IRC 152(b)(1) a return on which the filer (or, if joint, either
        # spouse) can be claimed has no dependents; Maryland requires such a
        # couple to file separate returns, where each spouse claims their own
        # exemption and they split "the overall number of dependents" of the
        # federal return. The federal exemption count applies exactly these
        # rules.
        md_personal_exemption = tax_unit("md_personal_exemption", period)
        exemptions = tax_unit("exemptions_count", period)
        return md_personal_exemption * exemptions
