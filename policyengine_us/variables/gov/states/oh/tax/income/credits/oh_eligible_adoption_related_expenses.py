from policyengine_us.model_api import *


class oh_eligible_adoption_related_expenses(Variable):
    value_type = float
    entity = Person
    label = "Ohio flag for calculating adoption related expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21",
        "https://tax.ohio.gov/wps/portal/gov/tax/help-center/faqs/income+-+individual+credits/income-individual-credits",
    )
    defined_for = StateCode.OH
