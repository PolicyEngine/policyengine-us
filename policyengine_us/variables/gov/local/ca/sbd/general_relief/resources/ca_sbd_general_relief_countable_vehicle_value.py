from policyengine_us.model_api import *


class ca_sbd_general_relief_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "San Bernardino County General Relief countable vehicle value"
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/39fc00fa-7256-4849-9f07-7710402996f1.docx",
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief.resources
        # Vehicle inputs exist only as household-level aggregates, so every
        # SPM unit in a shared household is charged the full household
        # vehicle value (the same convention as the riv/oc/smc county
        # programs).
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period)
        vehicle_value = household("household_vehicles_value", period)
        # The first $3,000 of each vehicle's net market value is exempt and
        # the balance counts toward the personal property limit. Only the
        # aggregate value and count are modeled, so the exemption is applied
        # as $3,000 x count against the total — this understates countable
        # value whenever a single vehicle is worth less than the exemption,
        # since its unused exemption shelters another vehicle's excess.
        # The county's rule evaluating a vehicle used as the principal
        # residence under the real property limit instead is not modeled;
        # every vehicle receives the personal property treatment.
        exempt_value = p.vehicle_exemption * vehicle_count
        return max_(vehicle_value - exempt_value, 0)
