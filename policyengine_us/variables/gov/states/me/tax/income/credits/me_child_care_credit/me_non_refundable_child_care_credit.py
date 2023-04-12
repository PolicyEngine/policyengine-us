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

    def formula(tax_unit, period, parameters):
        me_child_care_credit = tax_unit("me_child_care_credit", period)
        me_refundable_child_care_credit = tax_unit(
            "me_refundable_child_care_credit", period
        )

        return max_(me_child_care_credit - me_refundable_child_care_credit, 0)
