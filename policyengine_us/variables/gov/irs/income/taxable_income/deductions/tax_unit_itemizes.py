from policyengine_us.model_api import *


class tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes tax deductions"
    unit = USD
    documentation = "Whether this tax unit elects to itemize deductions, rather than claim standard deductions."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # First, apply a shortcut. We can't simulate SALT before federal income tax
        # (due to circular dependencies), but we can compare the deduction sizes assuming
        # the SALT is maxed out at its cap.
        ded = parameters(period).gov.irs.deductions
        federal_deductions_if_itemizing = ded.deductions_if_itemizing
        deductions_if_itemizing = [
            deduction
            for deduction in federal_deductions_if_itemizing
            if deduction
            not in [
                "salt_deduction",
                # Exclude QBID to avoid circular reference.
                "qualified_business_income_deduction",
            ]
        ]
        filing_status = tax_unit("filing_status", period)
        salt_cap = ded.itemized.salt_and_real_estate.cap[filing_status]
        itemized_deductions = (
            add(tax_unit, period, deductions_if_itemizing) + salt_cap
        )
        deductions_if_not_itemizing = tax_unit(
            "standard_deduction", period
        )  # Ignore QBID here, it requires SALT.
        if all(itemized_deductions < deductions_if_not_itemizing):
            return False

        tax_if_itemizing = tax_unit("tax_liability_if_itemizing", period)
        tax_if_not_itemizing = tax_unit(
            "tax_liability_if_not_itemizing", period
        )
        return tax_if_itemizing < tax_if_not_itemizing
