from policyengine_us.model_api import *


class long_term_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Long-term health insurance premiums"
    unit = USD
    definition_period = YEAR
    # No dataset fills this input, and no CMS series measures long-term care
    # insurance premiums. 26 U.S.C. 213(d)(10)(B) indexes the deductible
    # limits on these premiums by the medical care component of the CPI.
    uprating = "gov.bls.cpi.cpi_u_medical_care"
