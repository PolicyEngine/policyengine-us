from policyengine_us.model_api import *


class mortgage_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Qualified mortgage insurance premiums"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    documentation = (
        "Premiums paid for qualified mortgage insurance (from the Department "
        "of Veterans Affairs, the Federal Housing Administration, the Rural "
        "Housing Service, or private mortgage insurance) in connection with "
        "home acquisition debt on a qualified home, under a contract issued "
        "after 2006, and allocable to this year (Form 1098 box 5). Enter the "
        "premiums before any adjusted-gross-income phase-out."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#h_3_E",
        "https://www.law.cornell.edu/uscode/text/26/163#h_4_E",
    ]
