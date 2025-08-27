from datetime import timezone
from pathlib import Path
import sys

import hypothesis.strategies as st
from hypothesis import HealthCheck, assume, given, settings

sys.path.append(str(Path(__file__).resolve().parent.parent))
from main import calculate_duration


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    start=st.datetimes(timezones=st.sampled_from([timezone.utc])),
    end=st.datetimes(timezones=st.sampled_from([timezone.utc])),
)
def test_calculate_duration_property(start, end):
    assume(start <= end)
    result = calculate_duration(
        start.isoformat().replace("+00:00", "Z"),
        end.isoformat().replace("+00:00", "Z"),
    )
    delta = (end - start).total_seconds()
    assert result["seconds"] == int(delta)
    assert result["minutes"] == round(delta / 60, 2)
    assert result["hours"] == round(delta / 3600, 2)
