## line_45 form
from policyengine_us.model_api import *


class mi_alternate_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan alternate household credit"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR

    reference = (
        "https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/MI-1040CR7.pdf?rev=84f72df3f8664b96903aa6b655dc34d2"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
        )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit
        mi_household_resources = tax_unit("mi_household_resources", period)

        # determine heating cost
        mi_heating_cost = tax_unit("mi_heating_cost", period)

        # calculate alternate credit (tax form line 42)
        alternate_credit = min_(
            p.alternate_credit.upperlimit, mi_heating_cost
        )

        # calculate alternate credit difference (tax form line 44)
        difference = max_(
            (
                alternate_credit
                - mi_household_resources
                * p.total_household_resources.total_household_resources_rate_alternate
            ),
            0,
        )

        # determine mi_alternate_household_credit
        return p.alternate_credit.rate_amount * difference
