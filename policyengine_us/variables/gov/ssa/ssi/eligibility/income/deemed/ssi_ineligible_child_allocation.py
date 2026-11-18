from policyengine_us.model_api import *


class ssi_ineligible_child_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible child allocation"
    unit = USD
    documentation = (
        "The allocation SSI deducts for this child from an ineligible "
        "spouse's or parent's income before deeming it. Which claimants it "
        "applies to is decided where the allocations are summed."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1161#p-416.1161(c)",
        "https://www.ecfr.gov/current/title-20/section-416.1165#p-416.1165(b)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320185",
    )

    def formula(person, period, parameters):
        # Sum completed monthly budgets; supplied amounts retain their annual basis.
        return person("ssi_ineligible_child_allocation_monthly", period)
