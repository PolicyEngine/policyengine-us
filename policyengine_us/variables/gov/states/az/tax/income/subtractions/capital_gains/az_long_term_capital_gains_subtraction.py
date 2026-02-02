from policyengine_us.model_api import *


class az_long_term_capital_gains_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona long-term capital gains subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://www.azleg.gov/ars/43/01022.htm",
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=31",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.subtractions.capital_gains

        # Per ARS 43-1022(22): subtraction is for "net long-term capital gain
        # included in federal adjusted gross income". When there's an overall
        # capital loss, no LTCG is included in federal AGI.
        long_term_capital_gains = add(
            tax_unit, period, ["long_term_capital_gains"]
        )
        net_capital_gains = tax_unit("net_capital_gains", period)

        # Only include LTCG when there's a net capital gain overall
        ltcg_in_agi = where(
            net_capital_gains > 0,
            max_(0, long_term_capital_gains),
            0,
        )

        return ltcg_in_agi * p.rate
