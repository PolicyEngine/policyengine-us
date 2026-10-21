from policyengine_us.model_api import *


class ca_liheap_energy_burden_group(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = (
        "California LIHEAP supported local energy burden group (zero is unsupported)"
    )
    defined_for = StateCode.CA
    reference = (
        # PDF pages 257,282-283
        "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=257",
        "https://maderacap.org/wp-content/uploads/2025/10/Agenda-and-Packet-for-October-9-2025-Updated.pdf#page=191",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap
        local = p.local.madera
        cent = p.income.monthly_rounding_increment
        # Annual flows approximate a representative month. Restore each
        # monetary input's cents before truncating the percentage to basis points.
        cost_cents = sum(
            np.rint(spm_unit(source, period).astype(float) / cent).astype(np.int64)
            for source in p.energy_burden.expense_sources
        )
        income = spm_unit("ca_liheap_countable_income", period)
        income_cents = np.rint(income.astype(float) / cent).astype(np.int64)
        scale = int(np.rint(1 / p.energy_burden.rounding_increment))
        burden = np.floor_divide(cost_cents * scale, max_(income_cents, 1))
        county = spm_unit.household("county_str", period)
        supported = (
            np.isin(county, local.counties)
            & (income_cents > 0)
            & (cost_cents >= 0)
            & (cost_cents <= income_cents * local.maximum_energy_burden)
        )
        # Zero denotes missing policy coverage, not a first group or denial.
        return where(supported, local.energy_burden_group.calc(burden), 0)
