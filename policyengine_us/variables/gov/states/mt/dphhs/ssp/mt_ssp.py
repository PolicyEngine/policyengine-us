from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class mt_ssp(Variable):
    value_type = float
    entity = Person
    label = "Montana State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0520/chapter_0010/part_0010/section_0040/0520-0010-0010-0040.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#h",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320430#d",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-2025.htm",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ssp.amount
        category = person("mt_ssp_payment_category", period)
        # POMS SI 01415.058 H.2 pairs state codes G-K only with federal code A;
        # federal code D (a Title XIX facility) carries state code Z, so a
        # Medicaid-facility resident receives no supplement.
        federal_la = person("ssi_federal_living_arrangement", period)
        in_medicaid_facility = (
            federal_la == federal_la.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        individual = where(in_medicaid_facility, 0, p.individual[category])
        couple = where(in_medicaid_facility, 0, p.couple[category])
        # NOTE: SI DEN01415.010 B.3 lets Montana pay a recipient it places
        # outside Montana while keeping legal custody. PolicyEngine assigns
        # state supplements by the household's state, and the host state's
        # supplement would also apply, so this exception is not modeled.
        # NOTE: SI DEN01415.010 B.1 excludes section 1619(a) recipients and
        # section 1619 eligibles institutionalized throughout a month in a
        # medical facility. is_ssi_disabled already makes a disabled person
        # whose earnings exceed SGA SSI-ineligible, so the 1619(a) group
        # receives nothing here; a Title XIX facility resident falls under the
        # code D rule above, and other medical facilities are not modeled.
        # NOTE: The shared helper averages the spouses' couple rates, so a
        # joint couple with one spouse outside a certified setting splits half
        # the couple rate equally. SSA treats spouses who stop living together
        # as individuals from the month after the change (20 CFR 416.1801(c);
        # SI 00501.154), so such couples need separate marital units.
        # NOTE: The federal couple computation reads only aged, blind or
        # disabled status, so a spouse who declines SSI or is otherwise
        # ineligible still makes the claim joint (issue 10138).
        # NOTE: With an ineligible spouse, the helper pays the lesser of the
        # individual-rate amount on the claimant's own income and the
        # couple-rate amount on the deemed income; every Montana couple rate
        # exceeds the individual rate (SI 01320.430 D.3.b).
        # NOTE: The microdata do not record Montana's placement certification,
        # so this payment appears only in household calculations that set
        # mt_ssp_payment_category.
        return ssi_state_supplement(person, period, parameters, individual, couple)
