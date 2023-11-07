from policyengine_us.model_api import *


class taxsim_mstat(Variable):
    value_type = int
    entity = TaxUnit
    label = "Marital Status"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        fstatus = filing_status.possible_values
        return select(
            [
                filing_status == fstatus.SINGLE,
                filing_status == fstatus.HEAD_OF_HOUSEHOLD,
                filing_status == fstatus.JOINT,
                filing_status == fstatus.SEPARATE,
                filing_status == fstatus.WIDOW,
            ],
            [
                1,
                1,
                2,
                6,
                8,
            ],
        )
