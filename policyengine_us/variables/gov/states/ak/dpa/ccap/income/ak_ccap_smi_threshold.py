from policyengine_us.model_api import *


class ak_ccap_smi_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP monthly State Median Income eligibility threshold"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=907",
        "https://health.alaska.gov/media/okdlx2xm/alaska-fics.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        # Alaska CCAP uses the FICS-published AK SMI scale (derived from
        # 2015-2019 ACS estimates), not the federal HHS SMI table. The
        # threshold is 85% of the FICS monthly 100% SMI for the family
        # size. The FICS table publishes family sizes 2 through 15; a
        # 1-person SPMUnit has no published SMI value (FICS does not
        # publish a 1p column), and families above 15 use the size-15
        # amount.
        p = parameters(period).gov.states.ak.dpa.ccap.income
        size = spm_unit("spm_unit_size", period.this_year)
        monthly_smi = p.smi.amount.calc(size)
        return monthly_smi * p.smi_rate
