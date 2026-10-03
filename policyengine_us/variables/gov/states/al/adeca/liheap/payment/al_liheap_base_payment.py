from policyengine_us.model_api import *


class al_liheap_base_payment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP base heating payment"
    defined_for = StateCode.AL
    reference = "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=57"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.payment
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        base = select(
            [
                heating_type == fuel.PROPANE,
                heating_type == fuel.NATURAL_GAS,
                heating_type == fuel.ELECTRICITY,
                (heating_type == fuel.WOOD)
                | (heating_type == fuel.COAL)
                | (heating_type == fuel.KEROSENE),
            ],
            [
                p.base_amount.propane,
                p.base_amount.natural_gas,
                p.base_amount.electricity,
                p.base_amount.wood_coal_kerosene,
            ],
            default=0,
        )
        size = spm_unit("al_liheap_household_size", period)
        additional_people = clip(size - 1, 0, p.maximum_payment_household_size - 1)
        # Cross-state rows have band zero before defined_for masks the result;
        # keep the eager lookup within the published three bands.
        band = clip(spm_unit("al_liheap_income_band", period), 1, 3)
        amount = (
            base
            - p.income_band_reduction[band]
            + additional_people * p.additional_person_amount
        )
        # This compact representation reproduces Appendix D's entire matrix.
        # The manual's worked example on page 22 uses an older payment amount.
        # No published category was identified for fuel oil, solar, other, or
        # unspecified heat. Returning zero leaves those estimates incomplete;
        # it does not establish legal ineligibility, including heat in rent.
        return where(base > 0, amount, 0)
