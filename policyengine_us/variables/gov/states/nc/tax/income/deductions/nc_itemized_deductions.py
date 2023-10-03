from policyengine_us.model_api import *


class nc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions "
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        # Qualified Mortgage Interest and Real Estate Property Taxes.
        filing_status = tax_unit("filing_status", period)

        mortgage_interest = add(tax_unit, period, ["mortgage_interest"])
        pirs = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate
        property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            pirs.cap[filing_status],
        )
        pco = parameters(
            period
        ).gov.states.nc.tax.income.deductions.itemized.cap
        capped_mortage_and_property_taxes = min_(
            mortgage_interest + property_taxes, pco.mortgage_and_property_tax
        )

        # North Carolina specifies a state and local tax deduction cap which is currently not modeled in PolicyEngine

        other_deductions = add(
            tax_unit,
            period,
            ["charitable_deduction", "medical_expense_deduction"],
        )

        return capped_mortage_and_property_taxes + other_deductions
