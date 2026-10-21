from policyengine_us.model_api import *


class mt_additions(Variable):
    value_type = float
    entity = Person
    label = "Montana additions to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://web.archive.org/web/20220523051049/https://rules.mt.gov/gateway/Subchapterhome.asp?scn=42%2E15%2E2",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=4",
    )
    defined_for = StateCode.MT
    adds = "gov.states.mt.tax.income.additions.additions"
