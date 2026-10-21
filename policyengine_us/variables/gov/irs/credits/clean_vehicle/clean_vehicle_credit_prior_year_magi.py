from policyengine_us.model_api import *


class clean_vehicle_credit_prior_year_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified AGI for the year before a clean vehicle purchase"
    unit = USD
    documentation = (
        "Modified adjusted gross income for the preceding taxable year, as "
        "the new and used clean vehicle credits define it: adjusted gross "
        "income plus income excluded under 26 U.S.C. 911, 931 and 933 (Form "
        "8936 line 4). A filer meets the credits' income limit if either "
        "year's modified AGI does. Household and microsimulation inputs "
        "usually cover a single year, so reading the preceding year would "
        "return zero income and pass everyone; when not provided, this "
        "defaults to the current year's modified AGI, and the current year "
        "alone decides."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/30D#f_10_A",
        "https://www.law.cornell.edu/uscode/text/26/25E#b_1",
        "https://www.irs.gov/pub/irs-prior/f8936--2024.pdf#page=1",
    )
    adds = ["agi_plus_section_911_931_933_exclusions"]
