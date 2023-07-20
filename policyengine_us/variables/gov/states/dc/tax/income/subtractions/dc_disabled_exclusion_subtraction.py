from policyengine_us.model_api import *


class dc_disabled_exclusion_subtraction(Variable):
    value_type = float
    entity = Person
    label = "DC disabled exclusion subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2021_D-2440.pdf"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-2440.pdf"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        # determine disablity-related eligibility
        is_disabled = person("is_permanently_and_totally_disabled", period)
        gets_ssi = person("ssi", period) > 0
        gets_ssdi = person("social_security_disability", period) > 0
        disabled_eligible = is_disabled & (gets_ssi | gets_ssdi)
        # determine income-related eligibility
        INCOME_SOURCES = ["household_market_income", "household_benefits"]
        household_income = add(person.household, period, INCOME_SOURCES)
        p = parameters(period).gov.states.dc.tax.income.subtractions
        income_eligible = household_income < p.disabled_exclusion.income_limit
        # return subtraction amount if meet both eligibilty requirements
        subtraction_amount = p.disabled_exclusion.amount
        return (disabled_eligible & income_eligible) * subtraction_amount
