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
        # Per 10-144 C.M.R. Chapter 331, Appendix Charts (Table 2):
        # Different maximums for Adult Included vs Child Only cases
        p = parameters(period).gov.states.me.dhhs.tanf

        unit_size = spm_unit("spm_unit_size", period.this_year)
        is_child_only = spm_unit("me_tanf_child_only_case", period)

        # Cap at max unit size, then add incremental for larger households
        max_size = p.max_unit_size
        capped_size = min_(unit_size, max_size)
        additional_members = max_(unit_size - max_size, 0)

        # Look up base amount by case type
        adult_included_base = p.maximum_benefit.adult_included[capped_size]
        child_only_base = p.maximum_benefit.child_only[capped_size]
        base_amount = where(
            is_child_only, child_only_base, adult_included_base
        )

        # Add incremental amount for households larger than max size
        incremental = additional_members * p.maximum_benefit.each_additional

        return base_amount + incremental
