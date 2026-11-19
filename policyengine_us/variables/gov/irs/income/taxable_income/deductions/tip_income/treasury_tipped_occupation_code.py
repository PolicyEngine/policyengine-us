from policyengine_us.model_api import *


class treasury_tipped_occupation_code(Variable):
    value_type = int
    entity = Person
    label = "Treasury tipped occupation code for the tip income deduction"
    definition_period = YEAR
    reference = [
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf",
        "https://www.irs.gov/irb/2026-18_IRB#TD-10044",
    ]
    documentation = (
        "Treasury Tipped Occupation Code (TTOC) from 26 CFR 1.224-1(i). "
        "Use 0 if the person did not receive tips in "
        "a Treasury-listed tipped occupation."
    )
