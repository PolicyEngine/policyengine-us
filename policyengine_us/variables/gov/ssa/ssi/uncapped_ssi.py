from policyengine_us.model_api import *


class uncapped_ssi(Variable):
    value_type = float
    entity = Person
    label = "Uncapped SSI"
    unit = USD
    documentation = "Maximum SSI, less countable income (can be below zero)."
    definition_period = MONTH
    defined_for = "is_ssi_eligible"
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1382#b",
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(e)(2)",
    )

    def formula(person, period, parameters):
        amount = person("ssi_amount_if_eligible", period)
        countable_income = person("ssi_countable_income", period)
        uncapped = amount - countable_income
        # 20 CFR 416.1163(e)(2): 'Your SSI benefit under the deeming rules
        # cannot be higher than it would be if deeming did not apply.
        # Therefore, your benefit is the lesser of the amount computed under
        # the rules in paragraph (d)(2) of this section or the amount
        # remaining after we subtract only your own countable income from an
        # individual's Federal benefit rate.' Taking the lesser before the
        # zero floor keeps this consistent with the payment for programs
        # that read the shortfall below zero.
        without_deeming = person("uncapped_ssi_without_spousal_deeming", period)
        deeming_applies = person("is_ssi_spousal_deeming_applies", period.this_year)
        return where(deeming_applies, min_(uncapped, without_deeming), uncapped)
