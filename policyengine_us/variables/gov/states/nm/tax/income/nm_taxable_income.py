from policyengine_us.model_api import *


class nm_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        additions = tax_unit("nm_additions", period)
        salt_add_back = tax_unit("nm_salt_add_back", period)
        deductions = tax_unit("nm_deductions", period)
        exemptions = tax_unit("nm_exemptions", period)
        other_deductions_and_exemptions = tax_unit(
            "nm_other_deductions_and_exemptions", period
        )
        return max_(
            0,
            federal_agi
            + salt_add_back
            + additions
            - deductions
            - exemptions
            - other_deductions_and_exemptions,
        )
