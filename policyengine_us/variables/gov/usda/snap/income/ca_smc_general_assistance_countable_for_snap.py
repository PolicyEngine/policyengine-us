from policyengine_us.model_api import *


class ca_smc_general_assistance_countable_for_snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "San Mateo General Assistance countable as SNAP unearned income"
    unit = USD
    defined_for = "in_smc"
    reference = (
        # CalFresh MPP 63-502.141 and 63-502.2(b).
        "https://cdss.ca.gov/Portals/9/Regs/Man/Fsman/fsman05.docx",
        # Resolution 077291, item A, and board memo 26-290.
        "https://sanmateocounty.legistar.com/LegislationDetail.aspx?ID=4388449",
        "https://sanmateocounty.legistar.com/ViewReport.ashx?GID=659&GUID=LATEST&ID=94585&M=R&N=TextL5&Title=Board+Memo",
    )

    def formula(spm_unit, period):
        arrangement = spm_unit("ca_smc_general_assistance_living_arrangement", period)
        independent_living = (
            arrangement == arrangement.possible_values.INDEPENDENT_LIVING
        )
        # The county pays facilities as vendors for treatment and out-of-home
        # care. The model does not break those grants into payment components.
        grant = spm_unit("ca_smc_general_assistance", period)
        return where(independent_living, grant, 0)
