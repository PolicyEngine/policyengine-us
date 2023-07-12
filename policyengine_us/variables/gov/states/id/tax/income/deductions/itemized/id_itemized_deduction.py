from policyengine_us.model_api import *
import numpy as np


class id_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EIS00407/EIS00407_01-05-2023.pdf"
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf"
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.deductions.itemized
        itm_deds = [
            deduction
            for deduction in p.amount
            if deduction not in ["salt_deduction"]
        ]
        itm_deds_less_salt = add(tax_unit, period, itm_deds)
        # uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        medical_expense = add(tax_unit, period, ["medical_expense"])
        print(medical_expense)

        person = tax_unit.members
        earned_income = person("earned_income", period)
        medical_expense_deds = where(
            medical_expense - earned_income * p.medical_expense_rate > 0,
            medical_expense - earned_income * p.medical_expense_rate,
            0,
        )
        print(medical_expense_deds)

        itemized_deds_amt = (
            # itm_deds_less_salt + uncapped_property_taxes + medical_expense
            itm_deds_less_salt
            + medical_expense_deds
        )
        print(itemized_deds_amt)

        p = parameters(period).gov.states.id.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        # base standard deduction amount
        standard_deds_base_amt = p.amount[filing_status]
        print(standard_deds_base_amt)

        divided_amt = where(
            (itemized_deds_amt - standard_deds_base_amt) > 0,
            itemized_deds_amt - standard_deds_base_amt,
            0,
        )
        print(divided_amt)
        divisor = parameters(
            period
        ).gov.states.id.tax.income.deductions.divisor
        print(divisor)

        return np.floor(divided_amt / divisor)
