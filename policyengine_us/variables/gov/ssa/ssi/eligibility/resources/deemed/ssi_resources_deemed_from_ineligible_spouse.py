from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


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
        spouse = _ssi_spouse_index(person, period)
        # 416.1202(a): 'whether or not such resources are available'.
        return where(
            person("is_ssi_spousal_resource_deeming_applies", period),
            resources[np.maximum(spouse, 0)],
            0,
        )
