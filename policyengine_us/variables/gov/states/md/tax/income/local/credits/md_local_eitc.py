from policyengine_us.model_api import *


class md_local_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD local earned income credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=26",
    )

    def formula(tax_unit, period, parameters):
        # § 10-704(d): the credit against the county income tax equals the
        # lesser of the federal earned income credit multiplied by 10 times
        # the applicable county income tax rate, or the county income tax.
        p = parameters(period).gov.states.md.tax.income.credits.eitc.local
        federal_eitc = tax_unit("eitc", period)
        rate = tax_unit("md_applicable_local_tax_rate", period)
        uncapped = federal_eitc * p.rate_multiplier * rate
        local_tax = tax_unit("md_local_income_tax_before_credits", period)
        return min_(uncapped, local_tax)
