from policyengine_us.model_api import *


class long_term_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Long-term health insurance premiums"
    unit = USD
    definition_period = YEAR
    # No dataset fills this input, and CMS's health expenditure projections
    # have no long-term care insurance premium series. 26 U.S.C.
    # 213(d)(10)(B) indexes the deductible limits on these premiums by the
    # chained CPI-U medical care component for August; nobody projects that
    # index, so this uses CBO's projection of the CPI-U medical care
    # component, by calendar year, as a proxy.
    uprating = "gov.bls.cpi.cpi_u_medical_care"
