from policyengine_us.model_api import *


class id_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho taxable income"
    unit = USD
    documentation = "Idaho taxable income"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        agi = tax_unit("id_agi", period)
        deductions = tax_unit("id_deductions", period)
        conformity_deductions = tax_unit(
            "id_qualified_business_income_and_federal_schedule_1a_deductions",
            period,
        )
        return max_(0, agi - deductions - conformity_deductions)
