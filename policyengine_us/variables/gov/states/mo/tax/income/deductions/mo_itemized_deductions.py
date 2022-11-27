from policyengine_us.model_api import *


class mo_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Sum of Federal itemized deductions applicable to MO taxable income calculation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf",
        "https://dor.mo.gov/forms/4711_2021.pdf#page=11",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.141&bid=7212",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        gov = parameters(period).gov
        federal_deductions = [
            deduction
            for deduction in gov.irs.deductions.itemized_deductions
            if deduction
            # SALT and QBID both cause circular references.
            not in ["salt_deduction", "qualified_business_income_deduction"]
        ]
        added_deductions = gov.states.mo.tax.income.deductions.extra_itemized
        return add(tax_unit, period, federal_deductions + added_deductions)
