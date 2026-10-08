from policyengine_us.model_api import *


class ok_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP regular heating assistance"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-10(i)(1), 340:20-1-11(d).
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7-a.pdf",
    )

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("ok_liheap_eligible", period)
        amount = spm_unit("ok_liheap_matrix_amount", period)
        # The regular heating matrix has no actual-expense cap. Unsupported
        # direct fuels and the published roomer 4+ zero remain in the matrix.
        return eligible * amount
