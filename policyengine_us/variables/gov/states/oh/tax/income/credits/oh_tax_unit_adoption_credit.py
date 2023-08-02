from policyengine_us.model_api import *


class oh_tax_unit_adoption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio tax unit adoption credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # Ohio 2021 Instructions for Filing Original and Amended - Line 17 – Ohio Adoption Credit
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21",
        # Ohio Income - Individual Credits (Education, Displaced Workers & Adoption)
        "https://tax.ohio.gov/wps/portal/gov/tax/help-center/faqs/income+-+individual+credits/income-individual-credits",
    )
    defined_for = StateCode.OH
    adds = ["oh_adoption_credit"]
