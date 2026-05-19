from policyengine_us.model_api import *


class tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes tax deductions"
    unit = USD
    documentation = "Whether tax unit elects to itemize deductions rather than claim the standard deduction."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        standard_deduction = tax_unit("standard_deduction", period)
        itemized_deductions = tax_unit("itemized_taxable_income_deductions", period)
        if parameters(period).gov.simulation.branch_to_determine_itemization:
            # determine federal itemization behavior by comparing tax liability
            tax_liability_if_itemizing = tax_unit("tax_liability_if_itemizing", period)
            tax_liability_if_not_itemizing = tax_unit(
                "tax_liability_if_not_itemizing", period
            )
            # Use a small tolerance for floating-point comparison due to floating point imprecision
            TOLERANCE = 0.01
            federal_tax_equal = (
                np.abs(tax_liability_if_itemizing - tax_liability_if_not_itemizing)
                <= TOLERANCE
            )
            # When federal tax liabilities tie (typical at low/moderate income where
            # refundable credits absorb the tax), fall back to the federal-level
            # deduction comparison. This matches the non-branching path below and
            # the IRS / TaxAct / TAXSIM-comparison default of itemizing whenever
            # itemized deductions exceed the standard deduction.
            return where(
                federal_tax_equal,
                itemized_deductions > standard_deduction,
                tax_liability_if_itemizing < tax_liability_if_not_itemizing,
            )
        # determine federal itemization behavior by comparing deductions
        return itemized_deductions > standard_deduction
