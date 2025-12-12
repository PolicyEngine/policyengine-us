from policyengine_us.model_api import *


class va_subtractions_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia subtractions from federal adjusted gross income for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16",
    )
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        # Calculate person-specific subtractions
        # The main subtraction that varies by person is the age deduction
        age_deduction = person("va_age_deduction_person", period)

        # Other subtractions (disability, federal employee, military, etc.)
        # are calculated at the tax unit level by summing person-level amounts
        # For the purpose of calculating separate VAGI per person, we focus on
        # the age deduction which is the key subtraction that affects the
        # spouse tax adjustment calculation

        return age_deduction
