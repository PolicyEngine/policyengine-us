from policyengine_us.model_api import *


class absent_spouse_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Earned income of a married taxpayer's spouse who is not on the return"
    documentation = (
        "For a taxpayer who is married at the end of the year but does not "
        "file a joint return (a separate filer, or a separated filer who "
        "files as head of household), the spouse's earned income for the "
        "section 129(b)(1)(B) dependent care assistance limit, including any "
        "amount the spouse is deemed to earn as a student or as incapable of "
        "self-care under section 129(b)(2). The spouse is not a member of the "
        "tax unit, so the model has no other record of these earnings. If it "
        "is not supplied, it defaults to the earned income limit that applies "
        "without it (min_head_spouse_earned, the taxpayer's own earnings on a "
        "return that is not joint), which leaves the limit unchanged."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/129#b_1",
        "https://www.law.cornell.edu/uscode/text/26/129#b_2",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("min_head_spouse_earned", period)
