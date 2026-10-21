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
        # grants an ineligible spouse. An aged, blind or disabled spouse who
        # meets the immigration condition is tested as part of a couple under
        # 416.1205(b), with only the exclusions an eligible individual gets.
        # A spouse who fails SSI's citizenship or qualified-noncitizen
        # condition is 'not eligible for SSI benefits' (416.1160) whatever
        # their age or disability, so keeps the ineligible-spouse exclusions.
        immigration_status = person("immigration_status", period)
        could_be_eligible = person("is_ssi_aged_blind_disabled", period) & (
            (immigration_status == immigration_status.possible_values.CITIZEN)
            | person("is_ssi_qualified_noncitizen", period)
        )
        resources = where(
            could_be_eligible[spouse],
            person("ssi_countable_resources", period)[spouse],
            person("ssi_resources_for_deeming", period)[spouse],
        )
        return where(
            person("is_ssi_spousal_resource_deeming_applies", period),
            resources,
            0,
        )
