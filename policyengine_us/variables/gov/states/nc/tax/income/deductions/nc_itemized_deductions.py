from policyengine_us.model_api import *


class nc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions"
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        # Qualified Mortgage Interest and Real Estate Property Taxes, after the
        # $20,000 limitation shared by spouses (Schedule A line 5).
        capped_mortage_and_property_taxes = tax_unit(
            "nc_mortgage_and_property_tax_deduction", period
        )

        # North Carolina specifies a state and local tax deduction cap which is currently not modeled in PolicyEngine

        other_deductions = add(
            tax_unit,
            period,
            ["charitable_deduction", "medical_expense_deduction"],
        )

        return capped_mortage_and_property_taxes + other_deductions
