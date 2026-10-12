from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deeming import (
    ssi_ineligible_parents,
    ssi_parental_deeming_parent_allocation_total,
)


class ssi_parental_deeming_parent_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI living allowance for this person's ineligible parents"
    documentation = (
        "The allowance SSI deducts for the needs of this person's ineligible "
        "parents before deeming their income: the individual federal benefit "
        "rate for one parent, the couple rate for two, and a couple rate for "
        "each further pair and an individual rate for one left over, as when "
        "both natural parents and a stepparent live with the child."
    )
    unit = USD
    definition_period = YEAR
    defined_for = "is_ssi_income_deeming_child"
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1165#p-416.1165(d)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320500",
    )

    def formula(person, period, parameters):
        _, ineligible, _ = ssi_ineligible_parents(person, period)
        return ssi_parental_deeming_parent_allocation_total(
            parameters, period, np.sum(ineligible, axis=1)
        )
