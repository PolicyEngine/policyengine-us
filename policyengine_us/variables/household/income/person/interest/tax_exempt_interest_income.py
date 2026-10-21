from policyengine_us.model_api import *


class tax_exempt_interest_income(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt interest income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Interest income exempt from federal income tax. For California income "
        "tax, this is assumed to be from California state or local bonds unless "
        "ca_out_of_state_municipal_bond_interest is supplied. Enter the portion "
        "from other states' municipal bonds in that input as well as in this "
        "total; it is a subset of this income, not additional income. Without "
        "issuer-source data, the default California addback is zero."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/subtitle-A/chapter-1/subchapter-B/part-III"
    uprating = "calibration.gov.irs.soi.tax_exempt_interest_income"
