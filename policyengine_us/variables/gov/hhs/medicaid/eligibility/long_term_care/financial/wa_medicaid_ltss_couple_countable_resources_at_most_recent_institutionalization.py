from policyengine_us.model_api import *


class wa_medicaid_ltss_couple_countable_resources_at_most_recent_institutionalization(
    Variable
):
    value_type = float
    entity = Person
    label = (
        "Washington Medicaid LTSS couple resources at most recent institutionalization"
    )
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted historical snapshot of both spouses' total countable "
        "resources on the first day of the month in which the most recent "
        "continuous period of institutionalization began, under WAC "
        "182-513-1355(2)-(4). A break of at least 30 consecutive days "
        "requires a new resource determination under WAC "
        "182-513-1350(3)(b)(vi)(A): supply the new period's snapshot after "
        "re-entry and repeat it in each modeled month of that period. Set "
        "medicaid_ltss_is_initial_eligibility_determination to true for "
        "the new determination. Unlike the Texas and Delaware first-period "
        "snapshot, this input replaces earlier periods' snapshots. It is "
        "not the couple's resources at the application or determination "
        "date. The model does not reconstruct institutional history or "
        "adjudicate qualifying breaks."
    )
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1355",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1350",
    )
