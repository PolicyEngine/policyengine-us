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
        # get the parameters for calcualtions
        agi = tax_unit("adjusted_gross_income", period)
        misc = tax_unit("misc_deduction", period)

        p = parameters(period).gov.states.ms.tax.income.deductions.itemized

        # compute itemized deduction maximum less salt
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)

        # calculate miscellanous max amount
        misc_deduction = max_(misc, p.misc_deduction_fraction * agi)

        return itm_deds_less_salt + misc_deduction
