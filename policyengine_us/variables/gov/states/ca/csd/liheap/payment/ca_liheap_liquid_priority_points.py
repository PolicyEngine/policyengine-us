from policyengine_us.model_api import *


class ca_liheap_liquid_priority_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP priority points within supported liquid heating coverage"
    defined_for = "ca_liheap_liquid_heating_covered"
    reference = "https://maderacap.org/wp-content/uploads/2025/10/Agenda-and-Packet-for-October-9-2025-Updated.pdf#page=189,191,233,234"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.local.madera
        income_group = max_(spm_unit("ca_liheap_income_group", period), 1)
        burden_group = max_(spm_unit("ca_liheap_energy_burden_group", period), 1)
        age = spm_unit.members("age", period)
        # Categories apply once each to all members, including nonqualified
        # members. The two age scales include the overlapping age bonuses.
        child_points = p.child_points.calc(spm_unit.min(age))
        elderly_points = p.elderly_points.calc(spm_unit.max(age))
        disabled = add(spm_unit, period, ["is_disabled"]) > 0
        return (
            p.income_points[income_group]
            + p.burden_points[burden_group]
            + child_points
            + elderly_points
            + disabled * p.disability_points
        )
