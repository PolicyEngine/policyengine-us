from policyengine_us.model_api import *


class ca_smc_general_assistance_countable_property(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Mateo County General Assistance countable property"
    definition_period = YEAR
    defined_for = "in_smc"
    reference = (
        "https://www.smcgov.org/media/153295/download?inline=#page=2",
        "https://sanmateocounty.legistar.com/View.ashx?GUID=25359405-C9EB-4566-AE97-D927CC455B02&ID=9802358&M=F#page=2",
    )

    adds = "gov.local.ca.smc.general_assistance.property.sources"
