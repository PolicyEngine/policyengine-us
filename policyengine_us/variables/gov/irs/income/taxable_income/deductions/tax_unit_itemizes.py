from policyengine_us.model_api import *


class tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes tax deductions"
    unit = USD
    documentation = "Whether tax unit elects to itemize deductions rather than claim the standard deduction."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if parameters(period).simulation.branch_to_determine_itemization:
            # determine federal itemization behavior by comparing tax liability
            tax_liability_if_itemizing = tax_unit(
                "tax_liability_if_itemizing", period
            )
            tax_liability_if_not_itemizing = tax_unit(
                "tax_liability_if_not_itemizing", period
            )
            return tax_liability_if_itemizing < tax_liability_if_not_itemizing
        else:
            # determine federal itemization behavior by comparing deductions
            standard_deduction = tax_unit("standard_deduction", period)
            p = parameters(period).gov.irs.deductions
            itemized_deductions = add(tax_unit, period, p.itemized_deductions)
            return itemized_deductions > standard_deduction
