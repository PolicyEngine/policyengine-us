from policyengine_us.model_api import *


class ok_liheap_immigration_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets Oklahoma LIHEAP citizenship and immigration requirements"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-10(d) and 340:50-5-67(a).
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://www.ecfr.gov/current/title-7/section-273.4",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm",
    )

    def formula(person, period, parameters):
        # OAC 340:20-1-10(d)(3) admits "an alien who is both qualified and
        # eligible, per OAC 340:50-67". That cites the SNAP rule 340:50-5-67(a):
        # "Per Section 273.4 of Title 7 of the Code of Federal Regulations ...
        # to be eligible for food benefits a person must be:" the same four
        # categories as 340:20-1-10(d)(1)-(4). LIHEAP therefore follows SNAP
        # alien eligibility, including P.L. 119-21 sec. 10108, which limits
        # 7 U.S.C. 2015(f) to citizens and nationals, permanent residents,
        # Cuban and Haitian entrants and COFA residents from July 2025.
        # NOTE: The eCFR text of 7 CFR 273.4(a)(6) still lists refugees and
        # asylees; reading that unamended text would keep them eligible.
        # Noncitizen nationals and 273.4(a)(3)-(5) groups have no status value.
        # Annual eligibility uses the first month's circumstances.
        return person("is_snap_immigration_status_eligible", period.first_month)
