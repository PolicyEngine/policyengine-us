from policyengine_us.model_api import *


class pa_gambling_loss_offset(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania gambling losses offset against winnings"
    unit = USD
    documentation = (
        "The cost of tickets, bets and other wagers that Pennsylvania "
        "subtracts from the same person's gambling and lottery winnings "
        "(PA-40 Schedule T). Spouses may not use each other's costs, and the "
        "federal 90% limit does not apply. Noncash Pennsylvania Lottery "
        "prizes, which Pennsylvania does not tax, are not separated in the "
        "gambling inputs."
    )
    definition_period = YEAR
    reference = (
        # 72 P.S. 7303(a)(7)
        "https://www.legis.state.pa.us/WU01/LI/LI/US/PDF/1971/0/0002..PDF#page=123",
        # 2025 PA-40 Schedule T and its instructions
        # PDF pages 1, 3
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40t.pdf#page=1",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        winnings = person("gambling_winnings", period)
        losses = person("gambling_losses", period)
        return min_(losses, winnings)
