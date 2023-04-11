from policyengine_us.model_api import *


class ne_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        itax_before_credits = tax_unit("ne_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("ne_nonrefundable_credits", period)
        ne_amount = max_(0, itax_before_credits - nonrefundable_credits)
        # remaining calculations follow the Federal Tax Liability Worksheet
        ne_agi_additions = tax_unit("ne_agi_additions", period)
        ne_agi_subtractions = tax_unit("ne_agi_subtractions", period)
        add_less_sub = ne_agi_additions - ne_agi_subtractions
        p = parameters(period).gov.states.ne.tax.income
        adjustment = add_less_sub < p.credits.nonrefundable_adjust_limit
        us_amt = tax_unit("income_tax_before_credits", period)
        us_amount = where(adjustment, us_amt, ne_amount)
        return min_(ne_amount, us_amount)
