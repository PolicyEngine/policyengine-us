from policyengine_us.model_api import *


class ms_health_savings_account_adjustment(Variable):
    value_type = float
    entity = Person
    label = "Mississippi health savings account adjustment"
    unit = USD
    documentation = (
        "Each spouse's health savings account deduction (Form 80-105, the "
        "health savings account line of the adjustments, Column A for the "
        "taxpayer and Column B for the spouse). Mississippi excludes the "
        "amounts contributed to a health savings account from the account "
        "holder's gross income, so the tax unit's deduction is attributed once, "
        "to the account holders, rather than repeated for every member. The "
        "head and spouse get their own health_savings_account_ald_person "
        "amounts, scaled to sum to the tax unit's deduction; without them, the "
        "head takes it. A tax unit dependent has no deduction on this return."
    )
    definition_period = YEAR
    reference = (
        # Miss. Code Ann. § 71-9-11(3), enacted by H.B. 1213 (2005), sec. 2.
        "https://billstatus.ls.state.ms.us/documents/2005/html/HB/1200-1299/HB1213PS.htm",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80105228.pdf#page=2",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=6",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=13",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        filer_share = person_share_of_tax_unit_amount(
            person,
            period,
            "health_savings_account_ald",
            "health_savings_account_ald_person",
        )
        # The tax unit's deduction is the head's and spouse's; a dependent
        # takes no health savings account deduction (26 USC 223(b)(6)).
        return where(person("is_tax_unit_dependent", period), 0, filer_share)
