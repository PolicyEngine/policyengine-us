from policyengine_us.model_api import *


class dc_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Has eligible immigration status for DC Medicaid/Alliance"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = [
        "https://dhcf.dc.gov/alliance",
        "https://code.dccouncil.gov/us/dc/council/code/sections/1-307.03",
    ]
    documentation = """
    DC Health Care Alliance covers immigrants who are NOT eligible for
    federal Medicaid due to their immigration status. This includes
    undocumented immigrants, DACA recipients, and TPS holders.
    Citizens, LPRs, refugees, and other federally-eligible statuses
    should use federal Medicaid instead.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhcf.medicaid.eligibility
        immigration_status = person("immigration_status", period)

        # DC covers undocumented immigrants through Alliance program
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        dc_covers_undocumented = p.covers_undocumented

        # DC also covers DACA and TPS recipients (not federally eligible)
        daca_tps = immigration_status.possible_values.DACA_TPS
        daca = immigration_status.possible_values.DACA
        tps = immigration_status.possible_values.TPS
        daca_or_tps = (
            (immigration_status == daca_tps)
            | (immigration_status == daca)
            | (immigration_status == tps)
        )

        # Only return true for non-federally-eligible statuses
        # Citizens, LPRs, refugees, etc. should use federal Medicaid
        return (undocumented & dc_covers_undocumented) | daca_or_tps
