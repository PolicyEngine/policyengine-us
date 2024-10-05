from policyengine_us.model_api import *


class dc_disabled_exclusion_subtraction(Variable):
    value_type = float
    entity = Person
    label = "DC disabled exclusion subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55"
        # More details on page 56.
        "https://code.dccouncil.gov/us/dc/council/code/titles/47/chapters/18/subchapters/III"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        # Determine disablity-related eligibility
        is_disabled = person("is_permanently_and_totally_disabled", period)
        gets_ssi_or_ssdi = (
            add(person, period, ["ssi", "social_security_disability"]) > 0
        )
        disabled_eligible = is_disabled & gets_ssi_or_ssdi
        # Determine income-related eligibility
        p = parameters(
            period
        ).gov.states.dc.tax.income.subtractions.disabled_exclusion
        # Program counts AGI of all persons residing in a household, except
        # those under a written lease.
        # Assume tax unit for no
        tax_unit = person.tax_unit
        agi = tax_unit("adjusted_gross_income", period)
        income_eligible = agi < p.income_limit
        # Return subtraction amount if meet both eligibility requirements.
        # Use total household income, even that excluded from federal AGI.
        # Limit to IRS countable income as inclusion of benefits are unclear.
        household_gross_income = add(
            person.household, period, ["irs_gross_income"]
        )
        capped_amount = min_(household_gross_income, p.amount)
        return disabled_eligible * income_eligible * capped_amount
