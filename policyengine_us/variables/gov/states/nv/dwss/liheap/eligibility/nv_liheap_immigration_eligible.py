from policyengine_us.model_api import *


class nv_liheap_immigration_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets Nevada LIHEAP citizenship and immigration requirements"
    defined_for = StateCode.NV
    reference = (
        # PDF pages 21-23
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=21",
        # PDF pages 21-23
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=21",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nv.dwss.liheap.eligibility.five_year_bar
        # Section 302 A admits citizens and qualified non-citizens. PRUCOL,
        # COFA citizens, battered non-citizens and the other Section 302 A
        # groups without an immigration_status value are not identified.
        eligible_status = person("is_citizen_or_legal_immigrant", period)
        # Section 302 C bars a qualified non-citizen for five years after
        # entry unless an exemption applies. is_snap_alien_military_connected
        # applies the same veteran, active duty, spouse and unmarried
        # dependent child test (VII), and snap_alien_qualifying_quarters holds
        # the quarters count (VIII). People lawfully residing here and 65 or
        # older on August 22, 1996, tribal members, American Indians born in
        # Canada, Hmong and Highland Laotians, Amerasians and trafficking
        # victims have no input and are barred within five years of entry.
        # years_since_us_entry is read as years since an entry after August
        # 22, 1996.
        status = person("immigration_status", period)
        citizen = status == status.possible_values.CITIZEN
        exempt_status = np.isin(status.decode_to_str(), p.exempt_statuses)
        past_bar = person("years_since_us_entry", period) >= p.years
        child = person("age", period) < p.child_age_limit
        military = person("is_snap_alien_military_connected", period)
        lpr = status == status.possible_values.LEGAL_PERMANENT_RESIDENT
        quarters = person("snap_alien_qualifying_quarters", period)
        lpr_with_quarters = lpr & (quarters >= p.qualifying_quarters)
        not_barred = (
            citizen | exempt_status | past_bar | child | military | lpr_with_quarters
        )
        return eligible_status & not_barred
