from policyengine_us.model_api import *


class wa_ssp(Variable):
    value_type = float
    entity = Person
    label = "Washington State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0055",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-474-0012",
    )

    def formula(person, period, parameters):
        # MEDICAL_INSTITUTION rate note (effective 2023-07-01):
        # The rate equals the WA Apple Health institutional Personal Needs
        # Allowance (PNA) under WAC 182-513-1105(5) minus the $30 federal SSI
        # institutional PNA. The institutional PNA increases annually by SSA
        # COLA from 2024-01-01 per WAC 388-478-0057, so the SSP rate uprates
        # accordingly. Future maintainers updating the rate should consult
        # HCA Apple Health Income Standards rather than apply a mechanical
        # SSA-COLA to $70.
        category = person("wa_ssp_payment_category", period)
        return parameters(period).gov.states.wa.dshs.ssp.amount[category]
