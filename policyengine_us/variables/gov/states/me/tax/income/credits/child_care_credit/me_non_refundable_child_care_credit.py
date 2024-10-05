from policyengine_us.model_api import *


class me_non_refundable_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine non-refundable child care credit"
    unit = USD
    documentation = (
        "The portion of the Maine Child Care Credit that is non-refundable."
    )
    reference = [
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html",
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf#page=2",
    ]
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        child_care_credit = tax_unit("me_child_care_credit", period)
        refundable_child_care_credit = tax_unit(
            "me_refundable_child_care_credit", period
        )

        return max_(child_care_credit - refundable_child_care_credit, 0)
