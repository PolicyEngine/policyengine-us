from policyengine_us.model_api import *


class ssi_resources_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI resources deemed from an ineligible spouse"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(a)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330100",
    )

    def formula(person, period, parameters):
        resources = person("ssi_resources_for_deeming", period)
        ineligible = person("is_ssi_ineligible_spouse", period)
        spouse_resources = (
            person.marital_unit.sum(resources * ineligible) - resources * ineligible
        )
        # 416.1202(a): 'whether or not such resources are available'.
        return person("is_ssi_spousal_resource_deeming_applies", period) * max_(
            0, spouse_resources
        )
