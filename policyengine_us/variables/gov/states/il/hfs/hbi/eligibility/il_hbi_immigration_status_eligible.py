from policyengine_us.model_api import *


class il_hbi_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Has eligible immigration status for Illinois Health Benefits for Immigrants"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = [
        "https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html",
        "https://www.dhs.state.il.us/page.aspx?item=161600",
    ]
    documentation = """
    Illinois Health Benefits for Immigrants (HBI) covers residents who are not
    eligible for federal Medicaid due to their immigration status. This includes
    undocumented immigrants, DACA recipients, and TPS holders.

    As of May 1, 2024, Lawful Permanent Residents are NOT eligible for HBIA/HBIS
    (they may qualify for federal Medicaid after 5-year waiting period).
    """

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period)
        statuses = immigration_status.possible_values

        # Illinois covers undocumented immigrants
        undocumented = immigration_status == statuses.UNDOCUMENTED

        # Illinois also covers DACA and TPS recipients
        daca = immigration_status == statuses.DACA
        tps = immigration_status == statuses.TPS
        daca_tps = immigration_status == statuses.DACA_TPS

        # Only return true for non-federally-eligible statuses
        # Citizens, LPRs, refugees use regular federal Medicaid
        return undocumented | daca | tps | daca_tps
