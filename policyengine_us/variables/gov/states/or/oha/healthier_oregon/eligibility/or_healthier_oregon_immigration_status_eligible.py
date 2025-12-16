from policyengine_us.model_api import *


class or_healthier_oregon_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Has eligible immigration status for Oregon Healthier Oregon"
    definition_period = YEAR
    defined_for = StateCode.OR
    reference = [
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx",
        "https://olis.oregonlegislature.gov/liz/2021R1/Downloads/MeasureDocument/HB3352/Enrolled",
    ]
    documentation = """
    Oregon's Healthier Oregon program (formerly Cover All People) provides
    full OHP benefits to residents who are not eligible for federal Medicaid
    due to their immigration status. This includes undocumented immigrants,
    DACA recipients, and other non-qualifying immigration statuses.
    """

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period)

        # Oregon covers undocumented immigrants
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )

        # Oregon also covers DACA and TPS recipients
        daca = immigration_status == immigration_status.possible_values.DACA
        tps = immigration_status == immigration_status.possible_values.TPS
        daca_tps = (
            immigration_status == immigration_status.possible_values.DACA_TPS
        )

        # Only return true for non-federally-eligible statuses
        # Citizens, LPRs, refugees use regular federal Medicaid
        return undocumented | daca | tps | daca_tps
