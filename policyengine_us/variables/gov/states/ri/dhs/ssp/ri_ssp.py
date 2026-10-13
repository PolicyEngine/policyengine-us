from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_state_supplement,
)


class ri_ssp(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE40/40-6/40-6-27.htm",
        # 218-RICR-20-00-5, Sections 5.1.1 and 5.6
        # PDF pages 1, 13
        "https://risos-apa-production-public.s3.amazonaws.com/DHS/REG_13426_20260109151518643.pdf#page=1",
        # POMS SI BOS01415.012 B.1: Category D is for adult individuals only
        "https://secure.ssa.gov/poms.nsf/lnx/0501415012BOS",
        # POMS SI 01415.058 L: federally administered Category D payment level
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#l",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ssp.amount
        arrangement = person("ri_ssp_living_arrangement", period)
        arrangements = arrangement.possible_values
        # Category D applies to adult individuals only. A child or a member of
        # an eligible couple with certified care is paid as Category A (POMS
        # SI BOS01415.012 B.1; SI BOS01415.950 A.3).
        certified_care = arrangement == arrangements.RESIDENTIAL_CARE
        child = person("is_child", period.this_year)
        joint = person("ssi_couple_computation_applies", period)
        category_d = certified_care & ~child & ~joint
        own_household = certified_care & ~category_d
        individual = where(
            own_household, p.individual.INDEPENDENT, p.individual[arrangement]
        )
        couple = where(own_household, p.couple.INDEPENDENT, p.couple[arrangement])
        # SSA administers only Category D (218-RICR-20-00-5 Section 5.1.1.B).
        return ssi_state_supplement(
            person,
            period,
            parameters,
            individual,
            couple,
            federal_payment_rules=category_d,
        )
