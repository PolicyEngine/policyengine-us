from policyengine_us.model_api import *


class mi_ssp_person(Variable):
    value_type = float
    entity = Person
    label = "Michigan State Supplementary Payment per person"
    unit = USD
    definition_period = MONTH
    defined_for = "mi_ssp_eligible"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=2",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mi.html",
    )

    def formula(person, period, parameters):
        couple_eligible = person("mi_ssp_couple_eligible", period)
        base_amount = where(
            couple_eligible,
            person("mi_ssp_couple_amount", period),
            person("mi_ssp_individual_amount", period),
        )
        # Per SSA 2011 baseline: countable income deducts from federal SSI
        # first; any remaining countable income reduces the state
        # supplement. uncapped_ssi = SSI amount if eligible − countable
        # income; when countable exceeds the federal FBR, uncapped_ssi
        # goes negative and that negative magnitude is the residual income
        # to deduct from the SSP. uncapped_ssi has definition_period=YEAR
        # but unit=USD, so the framework auto-divides by 12 when accessed
        # from this MONTH formula via period.
        uncapped_ssi = person("uncapped_ssi", period)
        reduction = max_(0, -uncapped_ssi)
        return max_(0, base_amount - reduction)
