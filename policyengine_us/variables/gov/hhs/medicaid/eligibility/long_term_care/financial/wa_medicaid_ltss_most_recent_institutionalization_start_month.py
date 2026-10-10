from policyengine_us.model_api import *


class wa_medicaid_ltss_most_recent_institutionalization_start_month(Variable):
    value_type = int
    entity = Person
    label = "Washington Medicaid LTSS most recent continuous institutionalization start month"
    definition_period = MONTH
    default_value = 8
    documentation = (
        "Calendar month in which the most recent continuous period of "
        "institutionalization began. Together with the corresponding start "
        "year, this is the historical onset fact used by WAC "
        "182-513-1355(2)-(4), rather than a caller-selected allocation regime. "
        "The default year/month is August 2003, which preserves the modern "
        "floor/half/cap branch for existing callers who do not report history. "
        "Supply the actual onset for legacy continuous periods, and replace "
        "it after a break of at least 30 consecutive days. Repeat the onset "
        "in each modeled month of the continuous period. The statutory "
        "boundaries fall on the first day of a month, so no day input is needed."
    )
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1355",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1350",
    )
