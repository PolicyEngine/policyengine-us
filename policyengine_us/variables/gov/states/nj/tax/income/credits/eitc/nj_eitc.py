from policyengine_us.model_api import *


class nj_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get parameter tree for NJ EITC.
        p = parameters(period).gov.states.nj.tax.income.credits.eitc
        # Get parameter tree for federal EITC.
        p_fed = parameters(period).gov.irs.credits.eitc

        # Calculate NJ EITC.
        # If eligible for federal EITC, return federal EITC * percent_of_federal_eitc.
        # If ineligible for federal EITC only because of age, return (max federal EITC for zero children) * percent_of_federal_eitc.
        #     Note: this implies that they have no children.

        # Otherwise, return 0.
        # Worksheet reference: https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=43
        federal_eitc = select(
            [
                tax_unit("eitc_eligible", period),
                tax_unit("nj_childless_eitc_age_eligible", period),
            ],
            [
                tax_unit("eitc", period),
                p_fed.max.calc(0),
            ],
            default=0,
        )

        return federal_eitc * p.match
