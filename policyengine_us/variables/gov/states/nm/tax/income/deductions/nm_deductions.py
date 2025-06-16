from policyengine_us.model_api import *


class nm_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        itemized_on_federal_return = tax_unit("tax_unit_itemizes", period)
        itm_ded = tax_unit("total_itemized_taxable_income_deductions", period)
        standard_ded = tax_unit("standard_deduction", period)
        # Tax filer is required to itemize deductions if they itemize on their federal return as per:
        # https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf
        itemized_or_standard = where(
            itemized_on_federal_return,
            itm_ded,
            standard_ded,
        )
        OTHER_DEDUCTIONS = [
            "nm_medical_care_expense_deduction",
            "nm_deduction_for_certain_dependents",
            "nm_net_capital_gains_deduction",
        ]
        other_deductions = add(tax_unit, period, OTHER_DEDUCTIONS)
        return itemized_or_standard + other_deductions
