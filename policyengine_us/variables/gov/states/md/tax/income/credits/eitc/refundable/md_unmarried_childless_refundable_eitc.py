from policyengine_us.model_api import *


class md_unmarried_childless_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland unmarried childless refundable EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=19"
    defined_for = "md_qualifies_for_unmarried_childless_eitc"

    def formula(tax_unit, period, parameters):
        md_tax = tax_unit("md_income_tax_before_credits", period)
        md_unmarried_childless_non_refundable_eitc = tax_unit(
            "md_unmarried_childless_non_refundable_eitc", period
        )
        return max_(md_unmarried_childless_non_refundable_eitc - md_tax, 0)
