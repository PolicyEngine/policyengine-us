from policyengine_us.model_api import *


class nj_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey earned income tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get parameter tree for NJ EITC.
        p = parameters(period).gov.states.nj.tax.income.credits.eitc
        # Calculate NJ EITC.
        # If eligible for federal EITC, return federal EITC * percentage_of_federal_eitc.
        # If eligible for nj_childless_eitc_age_eligible above 18 and no qualyfing children, return p.amount
        # Otherwise, return 0.
        # Worksheet reference: https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=43
        nj_eitc = select(
            [
                tax_unit("eitc_eligible", period),
                tax_unit("nj_childless_eitc_age_eligible", period),
            ],
            [
                tax_unit("eitc", period) * p.percentage_of_federal_eitc,
                p.amount,
            ],
            default=0,
        )

        return nj_eitc


#
