
def test_racial_breakdowns():
    from policyengine_us import Microsimulation

    race = Microsimulation().calculate("race")
    assert (race == "WHITE").sum() > 0, "No people of racial category WHITE in the CPS"
    assert (race == "BLACK").sum() > 0, "No people of racial category BLACK in the CPS"
    assert (race == "HISPANIC").sum() > 0, "No people of racial category HISPANIC in the CPS"
    assert (race == "OTHER").sum() > 0, "No people of racial category OTHER in the CPS"