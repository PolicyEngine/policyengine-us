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
        heating_costs = tax_unit("heating_costs", period)

        # calculate alternate credit (tax form line 42)
        capped_heating_costs = min_(
            p.alternate_credit.heating_costs.max_amount, heating_costs
        )

        # calculate alternate credit difference (tax form line 44)
        difference = max_(
            (
                capped_heating_costs
                - mi_household_resources
                * p.alternate_credit.household_resources_rate
            ),
            0,
        )

        # determine mi_alternate_household_credit
        return p.alternate_credit.heating_costs.rate * difference
