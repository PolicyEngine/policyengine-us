from policyengine_us.model_api import *


class mt_additions(Variable):
    value_type = float
    entity = Person
    label = "Montana additions to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://rules.mt.gov/gateway/Subchapterhome.asp?scn=42%2E15%2E2",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=4",
    )
    defined_for = StateCode.MT
    adds = "gov.states.mt.tax.income.additions.additions"
