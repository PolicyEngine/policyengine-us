from policyengine_us.model_api import *


class oh_adoption_credit(Variable):
    value_type = float
    entity = Person
    label = "Ohio adoption credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # Ohio 2021 Instructions for Filing Original and Amended - Line 17 – Ohio Adoption Credit
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21",
        # Ohio Income - Individual Credits (Education, Displaced Workers & Adoption)
        "https://tax.ohio.gov/wps/portal/gov/tax/help-center/faqs/income+-+individual+credits/income-individual-credits",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        eligible_adoption_related_expenses = person(
            "oh_eligible_adoption_related_expenses", period
        )
        # The minimum amount of Ohio adoption credit
        min_credit = parameters(
            period
        ).gov.states.oh.tax.income.credits.adoption.minimum_credit

        # The maximum amount of Ohio adoption credit
        max_credit = parameters(
            period
        ).gov.states.oh.tax.income.credits.adoption.maximum_credit

        # Identify which interval the expenses fall into
        expenses_less_than_min_credit = (
            eligible_adoption_related_expenses < min_credit
        )
        expenses_between_min_and_max_credit = (
            min_credit <= eligible_adoption_related_expenses
        ) & (eligible_adoption_related_expenses <= max_credit)

        # expenses_between_min_and_max_credit = []
        # for i in eligible_adoption_related_expenses:
        #     expenses_between_min_and_max_credit.append(
        #         min_credit <= i <= max_credit
        #     )

        expenses_greater_than_max_credit = (
            eligible_adoption_related_expenses > max_credit
        )

        return (
            expenses_less_than_min_credit * min_credit
            + expenses_between_min_and_max_credit
            * eligible_adoption_related_expenses
            + expenses_greater_than_max_credit * max_credit
        )
