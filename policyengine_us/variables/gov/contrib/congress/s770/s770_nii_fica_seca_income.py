from policyengine_us.model_api import *


class s770_nii_fica_seca_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Already FICA or SECA covered income in supplied NII"
    documentation = "Validated amount already included in NII and taxed under section 1401 or 3101, other than the passive/already-SE intersection supplied separately. The active option removes it from broadened NII. Requires source classification; wages are not automatically subtracted from unrelated entity income."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
