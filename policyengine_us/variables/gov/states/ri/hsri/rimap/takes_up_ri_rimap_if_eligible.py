from policyengine_us.model_api import *


class takes_up_ri_rimap_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit takes up the Rhode Island Marketplace Affordability Program"
    definition_period = YEAR
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
    )
    documentation = (
        "HealthSource RI remits the subsidy to the insurer of an eligible "
        "enrollee's plan (R.I. Gen. Laws 42-157.2-4(b)), so a tax unit "
        "receives it when it enrolls in Marketplace coverage. This follows "
        "takes_up_aca_if_eligible unless supplied."
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("takes_up_aca_if_eligible", period)
