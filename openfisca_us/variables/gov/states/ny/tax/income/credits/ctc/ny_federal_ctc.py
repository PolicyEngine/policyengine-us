from openfisca_us.model_api import *


class ny_federal_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY federal CTC"
    unit = USD
    documentation = "The version of the federal ACTC used to determine the NY Empire State Child Credit."
    definition_period = YEAR
    defined_for = StateCode.NY

    formula = sum_of_variables(
        ["ny_federal_actc", "ny_federal_non_refundable_ctc"]
    )
