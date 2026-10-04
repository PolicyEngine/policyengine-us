from policyengine_us.model_api import *


class ca_liheap_covered_liquid_heating(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = (
        "California LIHEAP covered ordinary liquid heating component (check coverage)"
    )
    defined_for = "ca_liheap_liquid_heating_covered"
    reference = (
        "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=10,185,186,187,188",
        "https://maderacap.org/wp-content/uploads/2025/10/Agenda-and-Packet-for-October-9-2025-Updated.pdf#page=191,233,234",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap
        county = spm_unit.household("county_str", period)
        supported_county = np.isin(county, list(p.payment.liquid_base_amount))
        # defined_for masks after calculation; unrelated county keys must
        # still be safe to look up in mixed-state populations.
        safe_county = where(
            supported_county, county, next(iter(p.payment.liquid_base_amount))
        )
        income_group = max_(spm_unit("ca_liheap_income_group", period), 1)
        burden_group = max_(spm_unit("ca_liheap_energy_burden_group", period), 1)
        base = p.payment.liquid_base_amount[safe_county][income_group]
        size = spm_unit("ca_liheap_household_size", period)
        extra_people = clip(size - 1, 0, p.payment.maximum_payment_household_size - 1)
        age = spm_unit.members("age", period)
        vulnerable = (
            (p.local.madera.child_points.calc(spm_unit.min(age)) > 0)
            | (p.local.madera.elderly_points.calc(spm_unit.max(age)) > 0)
            | (add(spm_unit, period, ["is_disabled"]) > 0)
        )
        amount = (
            base
            + p.payment.additional_person_amount * extra_people
            + p.payment.liquid_burden_addition[burden_group]
            + p.payment.liquid_vulnerable_amount * vulnerable
        )
        eligible = spm_unit("ca_liheap_basic_eligible", period) & (
            spm_unit("ca_liheap_liquid_priority_points", period)
            >= p.local.madera.minimum_points
        )
        # Ordinary schedule only: no discretionary vendor-service supplement.
        # A zero with coverage=False is unsupported, not an entitlement denial.
        return where(
            eligible & supported_county,
            min_(amount, p.payment.liquid_maximum),
            0,
        )
