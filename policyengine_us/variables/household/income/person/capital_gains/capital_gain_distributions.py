from policyengine_us.model_api import *


class capital_gain_distributions(Variable):
    value_type = float
    entity = Person
    label = "capital gain distributions"
    unit = USD
    documentation = "Total capital gain distributions received, whether reported on Schedule D line 13 or directly on Form 1040 line 7 without a Schedule D."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 852(b)(3) - capital gain dividends",
        href="https://www.law.cornell.edu/uscode/text/26/852",
    )
    adds = [
        "schedule_d_capital_gain_distributions",
        "non_sch_d_capital_gains",
    ]
