from policyengine_us.model_api import *


class sd_liheap_base_payment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP direct-heating base payment component"
    defined_for = StateCode.SD
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/SD_BenefitMatrix_2026.pdf#page=1",
        # PDF pages 2, 4
        "https://dss.sd.gov/formsandpubs/docs/ENERGY/energyassistanceapplication.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.payment.direct
        region = spm_unit("sd_liheap_region", period)
        supported_region = (region >= 1) & (region <= 4)
        safe_region = clip(region, 1, 4)
        income = spm_unit("sd_liheap_countable_income", period)
        threshold = spm_unit("sd_liheap_income_threshold", period)
        tier = where(income <= threshold, 1, 2)
        heating_type = spm_unit("heating_type", period)
        fuels = heating_type.possible_values
        amount = select(
            [
                (heating_type == fuels.COAL) | (heating_type == fuels.WOOD),
                heating_type == fuels.ELECTRICITY,
                (heating_type == fuels.FUEL_OIL) | (heating_type == fuels.KEROSENE),
                heating_type == fuels.NATURAL_GAS,
                heating_type == fuels.PROPANE,
            ],
            [
                p.coal_wood[safe_region][tier],
                p.electricity[safe_region][tier],
                p.fuel_oil[safe_region][tier],
                p.natural_gas[safe_region][tier],
                p.propane[safe_region][tier],
            ],
            default=0,
        )
        # sd_liheap applies eligibility and caps vendor fuels at heating_expense,
        # read as unpaid seasonal vendor charges. An unknown region or SOLAR, OTHER
        # or UNSPECIFIED fuel returns zero as a coverage gap, not a denial (NONE
        # fails sd_liheap_eligible); the UNSPECIFIED default is tracked in #9754.
        return where(supported_region, amount, 0)
