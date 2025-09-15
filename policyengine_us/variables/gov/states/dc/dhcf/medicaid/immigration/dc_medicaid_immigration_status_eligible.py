from policyengine_us.model_api import *


class dc_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "DC Medicaid immigration status eligible"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = [
        "https://dhcf.dc.gov/alliance",
        "https://code.dccouncil.gov/us/dc/council/code/sections/1-307.03",
    ]

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhcf.medicaid.eligibility
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()

        # Check federal eligible immigration statuses
        federal_eligible_statuses = parameters(
            period
        ).gov.hhs.medicaid.eligibility.eligible_immigration_statuses
        federally_eligible = np.isin(
            immigration_status_str, federal_eligible_statuses
        )

        # DC covers undocumented immigrants through Alliance program
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        dc_covers_undocumented = p.covers_undocumented

        # DC also covers DACA and TPS recipients
        daca_tps = immigration_status.possible_values.DACA_TPS
        daca = immigration_status.possible_values.DACA
        tps = immigration_status.possible_values.TPS
        daca_or_tps = (
            (immigration_status == daca_tps)
            | (immigration_status == daca)
            | (immigration_status == tps)
        )

        return (
            federally_eligible
            | (undocumented & dc_covers_undocumented)
            | daca_or_tps
        )