from policyengine_us.model_api import *


class second_residence_mortgage_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Qualified mortgage insurance premiums on a second residence"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    documentation = (
        "Qualified mortgage insurance premiums paid in connection with "
        "acquisition debt on the taxpayer's second qualified residence (a "
        "residence other than the principal residence), allocable to this "
        "year, before any adjusted-gross-income phase-out. Do not include "
        "them in mortgage_insurance_premiums."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#h_3_E",
        "https://www.law.cornell.edu/uscode/text/26/163#h_5_A",
    ]
