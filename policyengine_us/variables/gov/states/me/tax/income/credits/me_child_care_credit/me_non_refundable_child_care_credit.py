from policyengine_us.model_api import *


class me_non_refundable_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "non-refundable ME Child Care Credit"
    unit = USD
    documentation = (
        "The portion of the ME Child Care Credit that is non-refundable."
    )
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf"
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html"
    definition_period = YEAR

    adds = ["me_child_care_credit"]
    subtracts = ["me_refundable_child_care_credit"]

    def formula(tax_unit, period, parameters):
        added_components = add(
            tax_unit, period, me_non_refundable_child_care_credit.adds
        )
        subtracted_components = add(
            tax_unit, period, me_non_refundable_child_care_credit.subtracts
        )

        return max_(added_components - subtracted_components, 0)
