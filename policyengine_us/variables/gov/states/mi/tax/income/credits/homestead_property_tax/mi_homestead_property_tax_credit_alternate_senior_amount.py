from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_alternate_senior_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Michigan alternate senior renter homestead property tax credit amount"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=34",
    )
    defined_for = "mi_homestead_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax
        senior = tax_unit("mi_is_senior_for_tax", period)
        # Line A
        allowable_credit_amount = tax_unit(
            "mi_homestead_property_tax_credit_pre_alternate_senior_amount",
            period,
        )
        # Line B
        rent = add(tax_unit, period, ["rent"])
        # Line C
        household_resources = tax_unit("mi_household_resources", period)
        applicable_resources = p.rate.senior.alternate * household_resources
        # Line D
        reduced_rent = max_(rent - applicable_resources, 0)
        senior_amount = max_(allowable_credit_amount, reduced_rent)
        capped_senior_amount = min_(senior_amount, p.cap)
        return senior * capped_senior_amount
