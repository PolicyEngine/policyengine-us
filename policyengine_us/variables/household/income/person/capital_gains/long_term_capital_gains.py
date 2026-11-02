from policyengine_us.model_api import *


class long_term_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "long-term capital gains"
    unit = USD
    documentation = (
        "Net gains made from sales of assets held for more than one year (losses "
        "are expressed as negative gains): Schedule D line 15, net of any "
        "long-term capital loss carryover, which long_term_capital_loss_carryover "
        "records as a memo."
    )
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(3)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#3",
    )
    adds = [
        "long_term_capital_gains_before_response",
        "capital_gains_behavioral_response",
    ]
