from policyengine_us.model_api import *


class de_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on the Delaware tax return"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        itax_indiv = add(
            tax_unit,
            period,
            ["de_income_tax_before_non_refundable_credits_indv"],
        )
        itax_joint = add(
            tax_unit,
            period,
            ["de_income_tax_before_non_refundable_credits_joint"],
        )
        return itax_indiv < itax_joint
