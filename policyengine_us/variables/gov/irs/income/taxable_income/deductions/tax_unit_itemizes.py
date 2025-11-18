from policyengine_us.model_api import *


class tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes tax deductions"
    unit = USD
    documentation = "Whether tax unit elects to itemize deductions rather than claim the standard deduction."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):

        if parameters(period).gov.simulation.branch_to_determine_itemization:
            # determine federal itemization behavior by comparing tax liability
            tax_liability_if_itemizing = tax_unit(
                "tax_liability_if_itemizing", period
            )
            tax_liability_if_not_itemizing = tax_unit(
                "tax_liability_if_not_itemizing", period
            )
            state_standard_deduction = tax_unit(
                "state_standard_deduction", period
            )
            state_itemized_deductions = tax_unit(
                "state_itemized_deductions", period
            )
            # Use a small tolerance for floating-point comparison due to floating point imprecision
            TOLERANCE = 0.01
            federal_tax_equal = (
                np.abs(
                    tax_liability_if_itemizing - tax_liability_if_not_itemizing
                )
                <= TOLERANCE
            )
            return where(
                federal_tax_equal,
                state_standard_deduction < state_itemized_deductions,
                tax_liability_if_itemizing < tax_liability_if_not_itemizing,
            )
        else:
            standard_deduction = tax_unit("standard_deduction", period)
            itemized_deductions = tax_unit(
                "itemized_taxable_income_deductions", period
            )
            # determine federal itemization behavior by comparing deductions
            return itemized_deductions > standard_deduction
