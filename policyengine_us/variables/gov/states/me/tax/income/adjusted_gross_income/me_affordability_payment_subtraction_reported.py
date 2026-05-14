from policyengine_us.model_api import *


class me_affordability_payment_subtraction_reported(Variable):
    value_type = float
    entity = TaxUnit
    label = "Reported Maine affordability payment subtraction"
    unit = USD
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=158"
    definition_period = YEAR
    defined_for = StateCode.ME
    documentation = (
        "User-reported portion of the Maine affordability payment that was "
        "included in federal adjusted gross income for tax years 2026 or "
        "2027. Sec. T-1, sub-§4 directs subtracting this amount from "
        "Maine income to the extent it was included in FAGI; the IRS has "
        "not yet ruled on whether the direct payment is federally taxable, "
        "so PolicyEngine accepts this as user input rather than computing "
        "it."
    )
