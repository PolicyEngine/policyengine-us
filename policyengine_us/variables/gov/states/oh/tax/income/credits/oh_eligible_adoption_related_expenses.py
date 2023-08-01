from policyengine_us.model_api import *


class oh_eligible_adoption_related_expenses(Variable):
    value_type = float
    entity = Person
    label = "Ohio eligible adoption-related expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        # Ohio 2021 Instructions for Filing Original and Amended - Line 17 – Ohio Adoption Credit
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21",
        # Ohio Income - Individual Credits (Education, Displaced Workers & Adoption)
        "https://tax.ohio.gov/wps/portal/gov/tax/help-center/faqs/income+-+individual+credits/income-individual-credits",
    )
    defined_for = StateCode.OH
