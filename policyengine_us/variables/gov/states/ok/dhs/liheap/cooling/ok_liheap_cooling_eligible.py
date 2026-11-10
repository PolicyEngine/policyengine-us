from policyengine_us.model_api import *


class ok_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Oklahoma LIHEAP summer cooling assistance"
    defined_for = StateCode.OK
    # OAC 340:20-1-10(b)(2), (e) and (h), 340:20-1-20(d): eligible size, the
    # gross income test heating uses, and responsibility for cooling costs.
    reference = (
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        # PDF pages 574-576, 588-589
        "https://oklahoma.gov/content/dam/ok/en/omma/content/rulemaking-process/rules/Register_Volume-42_Issue-20.pdf#page=574",
        # PDF pages 11-12
        "https://liheapch.acf.gov/docs/2026/state-plans/OK_Plan_2026.pdf#page=11",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ok_liheap_household_size", period)
        income_eligible = spm_unit("ok_liheap_income_eligible", period)
        # OAC 340:20-1-10(h)(1) requires total or partial responsibility for
        # home energy costs, here the cooling cost; a renter with utilities in
        # the rent qualifies through a verified surcharge (340:20-1-20(d)).
        responsible = spm_unit("has_cooling_expense", period)
        # The main cooling energy source is approved during the summer period
        # (340:20-1-10(b)(2)), so a home with no heating or any known heating
        # fuel qualifies; an unspecified fuel is paid $0, as in every LIHEAP
        # program (#9754).
        heating_type = spm_unit("heating_type", period)
        fuel_known = heating_type != heating_type.possible_values.UNSPECIFIED
        # Pre-authorization, roomer relatedness and tribal LIHEAP receipt have
        # no existing inputs.
        return (size > 0) & income_eligible & responsible & fuel_known
