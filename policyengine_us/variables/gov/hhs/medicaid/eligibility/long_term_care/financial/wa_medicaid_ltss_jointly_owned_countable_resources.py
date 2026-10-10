from policyengine_us.model_api import *


class wa_medicaid_ltss_jointly_owned_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Washington Medicaid LTSS applicant jointly owned countable resources"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Current full balance of countable resources held jointly in both spouses' names. "
        "This ownership fact is needed for continuous periods beginning "
        "before October 1, 1989: WAC 182-513-1355(2)(a) counts half of "
        "applicant-sole and jointly held resources, excluding spouse-sole "
        "resources. Supply both ownership inputs for that cohort, including "
        "the full joint balance rather than the applicant's attributed share. "
        "These ownership amounts are separate from the current attributed "
        "resource input used for modern periods; the model cannot infer "
        "legal title from that input. Applicable asset exclusions remain "
        "the caller's resource-inventory responsibility."
    )
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1355"
