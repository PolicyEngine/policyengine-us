from policyengine_us.model_api import *


class or_erdc_countable_self_employment_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Oregon ERDC countable self-employment income"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0035"
    )

    def formula(person, period, parameters):
        # OAR 414-175-0035(81)(e) counts gross self-employment receipts before
        # costs, and (81)(a) determines each business separately. PolicyEngine
        # only tracks tax-net self-employment earnings, so each source is
        # floored at zero to keep a business loss from offsetting other income;
        # this still understates income by netting out business costs.
        return (
            max_(person("self_employment_income", period), 0)
            + max_(person("sstb_self_employment_income", period), 0)
            + max_(person("farm_operations_income", period), 0)
        )
