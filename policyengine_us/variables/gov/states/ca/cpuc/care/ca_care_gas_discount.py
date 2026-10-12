from policyengine_us.model_api import *


class ca_care_gas_discount(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = USD
    label = "California CARE gas discount"
    documentation = (
        "California's CARE program discounts natural gas bills for eligible "
        "households, separately from its electricity discount. PG&E applies the "
        "rate to procurement and transportation charges, and SoCalGas to "
        "customer, commodity, and transportation charges; surcharges, the "
        "climate credit, taxes, and fees are not discounted, though CARE "
        "customers also skip part of "
        "the public purpose program surcharge. The model treats gas_expense as "
        "the bill before the discount and applies the rate to the whole bill, "
        "an approximation of the tariff discount. The model has no "
        "utility-territory input, so it applies the discount to every eligible "
        "California household with a gas expense."
    )
    reference = (
        "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program",
        # Ordering Paragraph 2: CARE discount raised from 15% to 20%.
        "https://docs.cpuc.ca.gov/word_pdf/FINAL_DECISION/7673.pdf#page=20",
        # Schedule GL-1: discount applies to procurement and transportation charges.
        "https://www.pge.com/tariffs/assets/pdf/tariffbook/GAS_SCHEDS_GL-1.pdf#page=1",
    )
    defined_for = "ca_care_eligible"

    def formula(household, period, parameters):
        expense = add(household, period, ["gas_expense"])
        p = parameters(period).gov.states.ca.cpuc.care
        return p.gas_discount * expense
