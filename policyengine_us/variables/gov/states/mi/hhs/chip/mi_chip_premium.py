from policyengine_us.model_api import *


class mi_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan MIChild annual premium"
    unit = USD
    documentation = (
        "Annual Michigan MIChild (separate CHIP) premium paid by the tax "
        "unit. One flat monthly premium per family covers all CHIP-eligible "
        "children."
    )
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = "https://www.michigan.gov/mdhhs/assistance-programs/healthcare/childrenteens/michild/qanda/michild-program-general-information"

    def formula(tax_unit, period, parameters):
        has_chip_member = add(tax_unit, period, ["is_chip_eligible"]) > 0
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.mi.hhs.chip
        return has_chip_member * p.premium.calc(income_level) * MONTHS_IN_YEAR
