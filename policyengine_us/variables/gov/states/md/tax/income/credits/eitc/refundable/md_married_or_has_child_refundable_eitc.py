from policyengine_us.model_api import *


class md_married_or_has_child_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland refundable EITC for filers who are married or have qualifying child"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=23"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Limited to filers who are married or have child
        does_not_qualify_for_unmarried_childless_eitc = ~tax_unit(
            "md_qualifies_for_unmarried_childless_eitc", period
        )

        federal_eitc = tax_unit("eitc", period)
        md_tax = tax_unit("md_income_tax_before_credits", period)
        p = parameters(
            period
        ).gov.states.md.tax.income.credits.eitc.refundable.married_or_has_child

        total_refundable_eitc_amount = federal_eitc * p.match
        applicable_refundable_eitc = max_(
            total_refundable_eitc_amount - md_tax, 0
        )

        return (
            does_not_qualify_for_unmarried_childless_eitc
            * applicable_refundable_eitc
        )
