from policyengine_us.model_api import *


class me_tanf_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF standard of need"
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

        # Select the child-only schedule when it is published and the
        # assistance unit has no included adult.
        adult_included = spm_unit("me_tanf_adult_included", period.this_year)
        adult_included_amount = p.standard_of_need.amount[capped_size]
        child_only_amount = p.standard_of_need.child_only_amount[capped_size]
        use_child_only_schedule = p.child_only_structure.in_effect & ~adult_included
        base_amount = where(
            use_child_only_schedule,
            child_only_amount,
            adult_included_amount,
        )

        # Add incremental amount for households larger than max size
        # Rule 125A publishes identical increments for both grant types.
        incremental = additional_members * p.standard_of_need.additional_person

        return base_amount + incremental
