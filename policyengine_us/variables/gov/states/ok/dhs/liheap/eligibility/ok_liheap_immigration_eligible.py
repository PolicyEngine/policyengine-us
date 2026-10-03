from policyengine_us.model_api import *


class ok_liheap_immigration_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets Oklahoma LIHEAP citizenship and immigration requirements"
    defined_for = StateCode.OK
    reference = (
        # Current OAC 340:20-1-10(d) incorporates 340:50-5-67(a), which
        # expressly references 7 CFR 273.4. The printed citation omits 5.
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://www.ecfr.gov/current/title-7/section-273.4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.eligibility
        status = person("immigration_status", period).decode_to_str()
        allowed_status = np.isin(status, p.eligible_immigration_statuses)
        # Reuse the incorporated CFR waiting rule independently of SNAP's
        # additional post-OBBB statutory status exclusions. The retrieved
        # FY2026/FY2027 CFR text retains refugee/asylee eligibility. No
        # LIHEAP instruction extending SNAP's new exclusions was found.
        waiting_period = person(
            "meets_snap_qualified_alien_waiting_period", period.first_month
        )
        # Annual eligibility uses the first month's circumstances. Existing
        # waiting-rule proxies and missing enum categories (including
        # noncitizen nationals, trafficking and battered-alien categories)
        # remain input limitations; no new immigration input is introduced.
        return allowed_status & waiting_period
