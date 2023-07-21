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
            # itemized deductions cannot be accurately calculated because
            #   the state_income_tax part of the salt_deduction must be
            #   ignored in order to avoid circular logic errors
            partial_itemized_deductions = tax_unit(
                "itemized_deductions_less_salt", period
            )
            # add back the possibly capped local real estate taxes,
            #   which have no circular logic problems
            filing_status = tax_unit("filing_status", period)
            p = parameters(period).gov.irs.deductions
            itemized_deductions = partial_itemized_deductions + min_(
                add(tax_unit, period, ["real_estate_taxes"]),
                p.itemized.salt_and_real_estate.cap[filing_status],
            )
            return itemized_deductions > standard_deduction
