from policyengine_us.model_api import *


class ky_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Kentucky tax return"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        taxable_income_indiv = add(tax_unit, period, ["ky_taxable_income_indiv"])

        taxable_income_joint = add(tax_unit, period, ["ky_taxable_income_joint"])
        return taxable_income_indiv < taxable_income_joint
