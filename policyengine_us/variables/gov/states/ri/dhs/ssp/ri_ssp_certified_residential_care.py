from policyengine_us.model_api import *


class ri_ssp_certified_residential_care(Variable):
    value_type = bool
    entity = Person
    label = "Certified for Rhode Island SSP residential care or assisted living"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        # 218-RICR-20-00-5, Section 5.2.B.2.a
        "https://risos-apa-production-public.s3.amazonaws.com/DHS/REG_13426_20260109151518643.pdf#page=3",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415012BOS",
        # POMS SI 01415.058 L.1: OS code D only for DHS-certified residents
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#l1",
    )
    documentation = "Screened, assessed and certified by DHS as residing in a residential care or assisted living facility, including residents exempt from certification because they received this payment level in October or November 1998."
