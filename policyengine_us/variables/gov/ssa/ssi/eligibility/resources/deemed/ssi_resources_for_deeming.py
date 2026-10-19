from policyengine_us.model_api import *


class ssi_resources_for_deeming(Variable):
    value_type = float
    entity = Person
    label = "Countable SSI resources of a spouse or parent for deeming"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330220",
    )

    def formula(person, period, parameters):
        # 416.1202(a)(1), (b)(1)(i): 'Pension funds' include IRAs and
        # work-related pension plans. ssi_countable_resources already excludes
        # retirement assets, the home, vehicle and other noncountable assets.
        resources = person("ssi_countable_resources", period)
        excluded = person("ssi_resource_deeming_excluded_military_resources", period)
        return max_(0, resources - max_(0, excluded))
