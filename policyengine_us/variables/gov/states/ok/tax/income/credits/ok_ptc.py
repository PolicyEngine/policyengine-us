from policyengine_us.model_api import *


class ok_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "OK property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/538-H-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf"
    )
    defined_for = StateCode.OK
    """
    def formula(tax_unit, period, parameters):

    Any person 65 years of age or older or any totally disabled person
    who is head of a household, a resident of and domiciled in this state
    during the entire preceding calendar year, and whose gross household
    income for such year does not exceed $12,000, may file a claim for
    property tax relief on the amount of property taxes paid on the
    household they occupied during the preceding calendar year.
    The credit may not exceed $200. Claim must be made on Form 538-H.
    """
