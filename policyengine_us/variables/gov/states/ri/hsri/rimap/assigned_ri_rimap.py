from policyengine_us.model_api import *


class assigned_ri_rimap(Variable):
    value_type = float
    entity = TaxUnit
    label = "Assigned Rhode Island Marketplace Affordability Program"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
    )
    documentation = (
        "The Rhode Island Marketplace Affordability Program amount for tax "
        "units that take it up, mirroring assigned_aca_ptc. The subsidy is "
        "remitted to the insurer of an enrollee in coverage through "
        "HealthSource RI (R.I. Gen. Laws 42-157.2-4(b) and (c)), so only a "
        "tax unit that enrolls receives it."
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("ri_rimap", period) * tax_unit(
            "takes_up_ri_rimap_if_eligible", period
        )
