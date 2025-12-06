from policyengine_us.model_api import *


class nj_additions(Variable):
    value_type = float
    entity = Person
    label = "New Jersey additions to gross income"
    unit = USD
    documentation = "Additions to New Jersey gross income per NJ Statute 54A:5-1. These are amounts added back to gross income that may have been excluded or deducted for federal purposes."
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040.pdf",  # Lines 28-38
    )
    defined_for = StateCode.NJ

    adds = "gov.states.nj.tax.income.additions"
