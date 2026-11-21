from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.aca_ptc_slcsp import (
    benchmark_premium,
)


class nm_puente_health_benchmark_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Puente Health benchmark premium"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = (
        # Addendum 2: "the SLCSP in the consumer's rating area is the
        # benchmark" (PY2026).
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/3527710a-f9f6-4e8f-9cd7-d9ea1010b653/Addendum%202_%20MAP%20P%26P%20Puente%20Health.pdf#page=3",
        # FINAL PY2027 MAP manual, Puente Health premium assistance parameter
        # 2: "calculated using the SLCSP".
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/b61d3073-c0e6-4426-bb40-4cfef26fdca4/FINAL%202027%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=8",
    )
    documentation = (
        "The monthly second-lowest-cost silver plan premium for the tax "
        "unit's Puente Health members, priced on their own: age-curve "
        "premiums, with only the three oldest of their children charged. "
        "Puente Health members fail the federal credit's immigration or "
        "income test, so slcsp and aca_ptc_slcsp, which price the federal "
        "enrollees, leave them out. In a family where some members get the "
        "federal credit and others Puente Health, the sources do not say how "
        "the benchmark is split; the model prices Puente Health on its own "
        "members, and the federal credit and base New Mexico Premium "
        "Assistance on theirs."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        year = period.this_year
        member = person("is_aca_tax_family_member", year)
        enrolled = person("nm_puente_health_member_eligible", year)
        return benchmark_premium(tax_unit, period, parameters, member, enrolled)
