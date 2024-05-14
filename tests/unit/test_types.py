import pytest
from pydantic import ValidationError

from pyschwab.types import PeriodFrequency


def test_valid_day_period():
    period_frequency = PeriodFrequency(period_type="day", period=2, frequency_type="minute", frequency=5)
    assert period_frequency.period_type == "day"
    assert period_frequency.period == 2
    assert period_frequency.frequency_type == "minute"
    assert period_frequency.frequency == 5

def test_default_values():
    period_frequency = PeriodFrequency()
    assert period_frequency.period_type == "day"
    assert period_frequency.period == 10
    assert period_frequency.frequency_type == "minute"
    assert period_frequency.frequency == 1

    period_frequency = PeriodFrequency(period_type="month")
    assert period_frequency.period == 1
    assert period_frequency.frequency_type == "weekly"
    assert period_frequency.frequency == 1

def test_invalid_period():
    with pytest.raises(ValidationError) as exc_info:
        PeriodFrequency(period_type="year", period=25)
    assert "Invalid period for period_type year, must be one of: [1, 2, 3, 5, 10, 15, 20]" in str(exc_info.value)

def test_invalid_frequency_type():
    with pytest.raises(ValidationError) as exc_info:
        PeriodFrequency(period_type="day", period=1, frequency_type="daily")
    assert "Invalid frequency_type for period_type day, must be one of: ['minute']" in str(exc_info.value)

def test_invalid_frequency():
    with pytest.raises(ValidationError) as exc_info:
        PeriodFrequency(period_type="day", period=1, frequency_type="minute", frequency=45)
    assert "Invalid frequency for frequency_type minute, must be one of: [1, 5, 10, 15, 30]" in str(exc_info.value)
