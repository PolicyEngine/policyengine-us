from policyengine_us.model_api import *


class ky_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Married couple file separately on the Kentucky tax return"
    definition_period = YEAR
    reference = "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        itax_indiv = add(
            tax_unit,
            period,
            ["ky_income_tax_before_non_refundable_credits_indiv"],
        )

        itax_joint = add(
            tax_unit,
            period,
            ["ky_income_tax_before_non_refundable_credits_joint"],
        )
        return itax_indiv < itax_joint
