from policyengine_us.model_api import *


class dc_ccsp_countable_railroad_benefits(Variable):
    value_type = float
    entity = Person
    label = "Railroad benefits counted by the DC Child Care Subsidy Program"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=13",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title45/html/USCODE-2023-title45-chap9-subchapIV-sec231a.htm",
    )
    documentation = (
        "The reported railroad total less annuities the Railroad Retirement Board "
        "awards for permanent disability."
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        total = person("railroad_benefits", period)
        disability = person("railroad_disability_benefits", period)
        return total - min_(max_(disability, 0), max_(total, 0))
