from policyengine_us.model_api import *


class ky_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky modified adjusted gross income for the family size tax credit"
    unit = USD
    documentation = (
        "Modified gross income on the filing path the tax unit elects. "
        "Spouses filing separately on a combined return treat a column's "
        "negative income as zero; a joint return does not."
    )
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=22",
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        files_separately = tax_unit("ky_files_separately", period)
        return where(
            files_separately,
            tax_unit("ky_modified_agi_if_separate", period),
            tax_unit("ky_modified_agi_if_joint", period),
        )
