from policyengine_us.model_api import *


class va_additions_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia additions to federal adjusted gross income for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=24",
    )
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        # Currently no person-specific additions are implemented
        # When additions are added, they should be calculated here
        # at the person level
        return 0
