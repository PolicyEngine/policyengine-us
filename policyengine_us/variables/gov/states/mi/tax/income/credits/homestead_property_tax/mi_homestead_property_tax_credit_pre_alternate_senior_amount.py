from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_pre_alternate_senior_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan homestead property tax credit per alternate senior credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-508",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=34",
    )
    defined_for = "mi_homestead_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax.reduction
        # Line 42
        total_household_resources = tax_unit("mi_household_resources", period)
        homestead_allowable_credit = tax_unit(
            "mi_allowable_homestead_property_tax_credit", period
        )
        # Line 43
        # The reduction is specified as going from 100% to 0% rather than vice-versa.
        excess = max_(total_household_resources - p.start, 0)
        increments = np.ceil(excess / p.increment)
        phase_out_rate = max_(1 - increments * p.rate, 0)
        # Line 44
        return phase_out_rate * homestead_allowable_credit
