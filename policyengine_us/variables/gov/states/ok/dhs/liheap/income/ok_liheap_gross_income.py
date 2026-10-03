from policyengine_us.model_api import *


class ok_liheap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP gross income including deemed contributions"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-11(a)(4), (b): deeming precedes the gross test.
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible = person("ok_liheap_immigration_eligible", period)
        eligible_income = spm_unit.sum(
            person("ok_liheap_countable_income", period) * eligible
        )
        # Select one representative per tax unit, including all-child units.
        # The tax-law head flag excludes children and would lose those groups.
        representative = person.get_rank(person.tax_unit, -person("age", period)) == 0
        deemed_income = spm_unit.sum(
            person.tax_unit("ok_liheap_deemed_income", period) * representative
        )
        # Oklahoma TANF is SPMUnit/MONTH. Count the cash aggregate once;
        # existing inputs do not allocate it to individual recipients.
        tanf = spm_unit("ok_tanf", period, options=[ADD])
        return max_(eligible_income + deemed_income + tanf, 0)
