from policyengine_us.model_api import *


class nc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions",
        # N.C. Gen. Stat. 105-153.5(a)(2)b
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # 2025 Form D-401 instructions, Form D-400 Schedule A lines 1 to 5
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=20",
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        # Qualified Mortgage Interest and Real Estate Property Taxes.
        filing_status = tax_unit("filing_status", period)

        # The mortgage interest allowed under section 163(h) of the Code, so
        # interest on acquisition debt above the federal limits is excluded.
        mortgage_interest = add(tax_unit, period, ["deductible_mortgage_interest"])
        pirs = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            pirs.cap[filing_status],
        )
        pco = parameters(period).gov.states.nc.tax.income.deductions.itemized.cap
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
