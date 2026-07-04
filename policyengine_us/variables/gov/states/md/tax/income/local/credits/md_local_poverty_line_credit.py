from policyengine_us.model_api import *


class md_local_poverty_line_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD local poverty line credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-709&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=26",
    )

    def formula(tax_unit, period, parameters):
        # § 10-709(d): the credit against the county income tax equals the
        # lesser of the county income tax after subtracting the local earned
        # income credit, or the county income tax rate multiplied by the
        # eligible low income taxpayer's earned income.
        eligible = tax_unit("is_eligible_md_poverty_line_credit", period)
        earnings = tax_unit("tax_unit_earned_income", period)
        rate = tax_unit("md_applicable_local_tax_rate", period)
        earnings_portion = earnings * rate
        local_tax = tax_unit("md_local_income_tax_before_credits", period)
        local_eitc = tax_unit("md_local_eitc", period)
        remaining_tax = max_(local_tax - local_eitc, 0)
        return eligible * min_(earnings_portion, remaining_tax)
