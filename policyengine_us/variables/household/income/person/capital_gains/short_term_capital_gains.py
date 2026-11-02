from policyengine_us.model_api import *


class short_term_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "short-term capital gains"
    unit = USD
    documentation = (
        "Net gains made from sales of assets held for one year or less (losses "
        "are expressed as negative gains): Schedule D line 7, net of any "
        "short-term capital loss carryover, which short_term_capital_loss_carryover "
        "records as a memo."
    )
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(1)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#1",
    )
    uprating = "calibration.gov.irs.soi.short_term_capital_gains"
