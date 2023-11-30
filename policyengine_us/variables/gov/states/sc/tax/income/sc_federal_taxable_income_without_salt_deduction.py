from policyengine_us.model_api import *


class sc_federal_taxable_income_without_salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina federal taxable income excluding SALT"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf#page=2",  # line 1
        "https://dor.sc.gov/forms-site/Forms/SC1040inst_2022.pdf#page=2",
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1110
    )

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        standard_deduction = tax_unit("standard_deduction", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        itemized_deductions_less_salt = tax_unit(
            "itemized_deductions_less_salt", period
        )
        deductions = where(
            itemizes, itemized_deductions_less_salt, standard_deduction
        )
        return max_(0, agi - deductions)
