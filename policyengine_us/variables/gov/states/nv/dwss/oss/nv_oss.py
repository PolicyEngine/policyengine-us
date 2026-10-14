from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class nv_oss(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Nevada Optional State Supplementation"
    defined_for = StateCode.NV
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#i",
        "https://www.leg.state.nv.us/NRS/NRS-422A.html#NRS422ASec070",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-2025.htm",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320430#d",
        "https://secure.ssa.gov/poms.nsf/lnx/0502005030#g",
        "https://secure.ssa.gov/poms.nsf/lnx/0502001005",
        "https://secure.ssa.gov/poms.nsf/lnx/0502001010",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nv.dwss.oss.payment
        arrangement = person("nv_oss_living_arrangement", period)
        category = person("ssi_category", period.this_year)
        # SSA administers Nevada's supplement (SI 01415.058 A), so the federal
        # rounding and $1 minimum apply. Half of each member's same-category
        # couple rate reproduces all mixed-category totals in SI 01415.058 I.2.b.
        # Every Nevada couple rate is at least the individual rate, so spouse
        # deeming compares against the couple rate (SI 01320.430 D.3.b).
        # NOTE: couples living apart in different Nevada arrangements cannot
        # be modeled, because the federal framework has no living-apart status.
        return ssi_state_supplement(
            person,
            period,
            parameters,
            p.individual[arrangement][category],
            p.couple[arrangement][category],
        )
