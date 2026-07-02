from policyengine_us.model_api import *


class schedule_d_capital_gain_distributions(Variable):
    value_type = float
    entity = Person
    label = "Schedule D capital gain distributions"
    unit = USD
    documentation = "Capital gain distributions from regulated investment companies and REITs reported on Schedule D line 13. Memo component of long_term_capital_gains — already included there, so it does not separately enter gross income."
    definition_period = YEAR
    reference = dict(
        title="2024 Instructions for Schedule D (Form 1040), line 13",
        href="https://www.irs.gov/instructions/i1040sd",
    )
