from policyengine_us.model_api import *


class oh_adoption_credit(Variable):
    value_type = float
    entity = Person
    label = "Ohio adoption credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21",
        "https://tax.ohio.gov/wps/portal/gov/tax/help-center/faqs/income+-+individual+credits/income-individual-credits",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        eligible_adoption_related_expenses = person(
            "oh_eligible_adoption_related_expenses", period
        )
        min_credit = parameters(
            period
        ).gov.states.oh.tax.income.credits.adoption.minimum_credit
        max_credit = parameters(
            period
        ).gov.states.oh.tax.income.credits.adoption.maximum_credit
        expenses_less_than_min_credit = (
            eligible_adoption_related_expenses < min_credit
        )
        expenses_between_min_and_max_credit = (
            min_credit <= eligible_adoption_related_expenses <= max_credit
        )
        expenses_greater_than_max_credit = (
            eligible_adoption_related_expenses > max_credit
        )

        return (
            expenses_less_than_min_credit * min_credit
            + expenses_between_min_and_max_credit
            * eligible_adoption_related_expenses
            + expenses_greater_than_max_credit * max_credit
        )
