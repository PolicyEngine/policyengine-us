from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class nj_ssp(Variable):
    value_type = float
    entity = Person
    label = "New Jersey State Supplementary Payment"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#j",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415025NY",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320430#d",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/nj.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ssp.amount
        # NOTE: The C rate uses the federal ineligible-spouse definition, which
        # omits an aged, blind or disabled spouse who is ineligible for SSI or
        # chooses not to apply (SI 01415.058 J.1); the model treats that claim
        # as joint and pays half the couple rate instead.
        arrangement = person("nj_ssp_living_arrangement", period)
        # NOTE: The shared helper averages the couple rates of spouses in
        # different arrangements. SSA treats spouses who enter an institution
        # as two individuals after the month of change (SI NY01415.025), so
        # such couples need explicit marital-unit inputs.
        # NOTE: The individual rate exceeds the couple rate for codes B and C,
        # so a claim with deemed spousal income uses the higher individual
        # rate (SI 01320.430 D.2.c).
        # NOTE: Every rate except the Medicaid-facility rate includes the
        # state's Lifeline utility payment (SI 01415.058 J.1); issue 10230
        # tracks counting it net of the Lifeline in New Jersey LIHEAP.
        return ssi_state_supplement(
            person, period, parameters, p.individual[arrangement], p.couple[arrangement]
        )
