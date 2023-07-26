from policyengine_us.model_api import *


class ms_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi itemized deduction"
    unit = USD
    definition_period = YEAR

    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15"
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf"
    )
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # compute itemized deduction maximum
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)

        # calculate itemized deductions total amount
        exempt_deds = add(
            tax_unit,
            period,
            [
                "itemized_taxable_income_deductions",
                "misc_deduction",
            ],
        )

        return exempt_deds + itm_deds_less_salt
