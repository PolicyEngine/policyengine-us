from policyengine_us.model_api import *


class az_itemized_deductions_less_salt(Variable):
    value_type = float
    entity = TaxUnit
    label = " Total federal itemized deductions allowed to be taken on federal return"
    unit = USD
    documentation = "Arizona Form 140 Schedule A Form 140"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://azdor.gov/forms/individual/itemized-deduction-adjustments-form"
        "https://azdor.gov/forms/individual/form-140-resident-personal-income-tax-form-calculating"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        return add(tax_unit, period, itm_deds)