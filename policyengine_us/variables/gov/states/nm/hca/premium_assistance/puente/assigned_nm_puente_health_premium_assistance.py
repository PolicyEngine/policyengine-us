from policyengine_us.model_api import *


class assigned_nm_puente_health_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Assigned New Mexico Puente Health premium assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        # Addendum 2, Section I: Puente Health "only applies to plans sold on
        # BeWell's individual market platform", so it reaches only enrollees.
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/3527710a-f9f6-4e8f-9cd7-d9ea1010b653/Addendum%202_%20MAP%20P%26P%20Puente%20Health.pdf#page=2",
        # FINAL PY2027 MAP manual, Puente Health Program: the same limit to
        # plans sold on BeWell.
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/b61d3073-c0e6-4426-bb40-4cfef26fdca4/FINAL%202027%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=7",
    )
    documentation = (
        "Puente Health premium assistance for tax units that take it up, "
        "mirroring assigned_aca_ptc and assigned_nm_premium_assistance. This "
        "is the amount the household health benefit totals count."
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("nm_puente_health_premium_assistance", period) * tax_unit(
            "takes_up_nm_puente_health_if_eligible", period
        )
