from policyengine_us.model_api import *


class mo_ssp_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Missouri SSP citizenship and immigrant status requirement"
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0405-000-00/0405-030-00/",
        "https://web.archive.org/web/20250809181856/https://dssmanuals.mo.gov/december-1973-eligibility-requirements/1010-000-00/",
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0605-000-00/0605-010-00/",
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/1805-020-10-10/1805-020-10-10-05/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/1805-020-10-10/1805-020-10-10-10/",
    )

    def formula(person, period, parameters):
        # SAB (§ 0405.030.00) and SNC, which uses the December 1973
        # requirements (SNC § 0605.010.00; December 1973 § 1010.000.00), apply
        # the MO HealthNet for Families citizenship and immigrant status rules
        # of § 1805.020.10, which have not been amended for the October 2026
        # federal Medicaid changes.
        p = parameters(period).gov.states.mo.dss.ssp.eligibility.immigration
        status = person("immigration_status", period)
        status_str = status.decode_to_str()
        citizen = status == status.possible_values.CITIZEN
        qualified = np.isin(status_str, p.qualified_statuses)
        no_waiting_period = np.isin(status_str, p.no_waiting_period_statuses)
        waited = person("years_since_us_entry", period) >= p.waiting_period
        # § 1805.020.10.10.10 waives the waiting period for veterans and
        # active-duty members. Not modeled: the same waiver for their spouses,
        # dependent children, and unmarried surviving spouses, and the 8 USC
        # 1622(b)(2) exemption for permanent residents with 40 qualifying
        # quarters. Those immigrants within five years of entry are treated as
        # ineligible.
        military = person("is_veteran", period) | person("is_military", period)
        return citizen | (qualified & (no_waiting_period | waited | military))
