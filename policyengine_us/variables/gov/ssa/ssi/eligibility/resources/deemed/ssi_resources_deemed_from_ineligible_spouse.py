from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ssi_resources_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI resources counted from a spouse"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(a)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330100",
    )

    def formula(person, period, parameters):
        spouse = np.maximum(_ssi_spouse_index(person, period), 0)
        # 416.1202(a): an ineligible spouse's resources count 'whether or not
        # such resources are available', less the exclusions 416.1202(a)(2)
        # grants an ineligible spouse. An aged, blind or disabled spouse is
        # tested as part of a couple under 416.1205(b), with only the
        # exclusions an eligible individual gets.
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        resources = where(
            aged_blind_disabled[spouse],
            person("ssi_countable_resources", period)[spouse],
            person("ssi_resources_for_deeming", period)[spouse],
        )
        return where(
            person("is_ssi_spousal_resource_deeming_applies", period),
            resources,
            0,
        )
