from policyengine_us.model_api import *


class me_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 10-144 C.M.R. Chapter 331, Appendix Charts (Table 2)
        p = parameters(period).gov.states.me.dhhs.tanf

        unit_size = spm_unit("spm_unit_size", period.this_year)

        # Cap at max unit size, then add incremental for larger households
        max_size = p.max_unit_size
        capped_size = min_(unit_size, max_size)
        additional_members = max_(unit_size - max_size, 0)

        # Look up base amount
        base_amount = p.maximum_benefit.amount[capped_size]

        # Add incremental amount for households larger than max size
        incremental = additional_members * p.maximum_benefit.additional_person

        return base_amount + incremental
