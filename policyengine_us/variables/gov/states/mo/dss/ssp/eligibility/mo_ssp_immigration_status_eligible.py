from policyengine_us.model_api import *


class mo_ssp_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Missouri SSP citizenship and immigrant status requirement"
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0405-000-00/0405-030-00/",
        "https://web.archive.org/web/20220519212253/https://dssmanuals.mo.gov/december-1973-eligibility-requirements/1010-000-00/",
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0605-000-00/0605-010-00/",
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/",
    )

    def formula(person, period, parameters):
        # SAB (§ 0405.030.00) and SNC, which uses the December 1973
        # requirements (SNC § 0605.010.00; December 1973 § 1010.000.00), apply
        # the MO HealthNet for Families citizenship and immigrant status rules
        # of § 1805.020.10, which have not been amended for the October 2026
        # federal Medicaid changes. Not modeled: the five-year waiting period
        # for permanent residents, parolees, and conditional entrants
        # (§ 1805.020.10.10.10), and its exception for veterans, active-duty
        # members, and their spouses and dependent children.
        p = parameters(period).gov.states.mo.dss.ssp.eligibility.immigration
        status = person("immigration_status", period)
        citizen = status == status.possible_values.CITIZEN
        qualified = np.isin(status.decode_to_str(), p.qualified_statuses)
        return citizen | qualified
