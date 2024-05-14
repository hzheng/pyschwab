from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PeriodFrequency(BaseModel):
    period_type: str = Field(default="day", description="The chart period being requested", json_schema_extra={"example": "day"})
    period: Optional[int] = Field(None, description="The number of chart period types", json_schema_extra={"example": 10})
    frequency_type: Optional[str] = Field(None, description="The time frequencyType", json_schema_extra={"example": "minute"})
    frequency: Optional[int] = Field(None, description="The time frequency duration", json_schema_extra={"example": 1})

    @field_validator('period_type')
    def validate_period_type(cls, v):
        if v not in ['day', 'month', 'year', 'ytd']:
            raise ValueError('Invalid period_type, must be one of: day, month, year, ytd')
        return v

    @model_validator(mode="before")
    def set_defaults(cls, values):
        if values.get('period_type') is None:
            values['period_type'] = 'day'
        if values.get('period') is None:
            default_periods = {
                'day': 10,
                'month': 1,
                'year': 1,
                'ytd': 1
            }
            values['period'] = default_periods.get(values.get('period_type'))

        if values.get('frequency_type') is None:
            default_frequency_types = {
                'day': 'minute',
                'month': 'weekly',
                'year': 'monthly',
                'ytd': 'weekly'
            }
            values['frequency_type'] = default_frequency_types.get(values.get('period_type'))

        if values.get('frequency') is None:
            values['frequency'] = 1

        return values

    @field_validator('period')
    def validate_period(cls, v, info):
        if 'period_type' in info.data:
            valid_periods = {
                'day': [1, 2, 3, 4, 5, 10],
                'month': [1, 2, 3, 6],
                'year': [1, 2, 3, 5, 10, 15, 20],
                'ytd': [1]
            }
            period_type = info.data['period_type']
            valid_period = valid_periods.get(period_type, None)
            if not valid_period:
                raise ValueError(f'Invalid period type: {period_type}')
            if v not in valid_period:
                raise ValueError(f'Invalid period for period_type {period_type}, must be one of: {valid_period}')
        return v

    @field_validator('frequency_type')
    def validate_frequency_type(cls, v, info):
        if 'period_type' in info.data:
            valid_frequency_types = {
                'day': ['minute'],
                'month': ['daily', 'weekly'],
                'year': ['daily', 'weekly', 'monthly'],
                'ytd': ['daily', 'weekly']
            }
            period_type = info.data['period_type']
            valid_frequency_type = valid_frequency_types.get(period_type, None)
            if not valid_frequency_type:
                raise ValueError(f'Invalid period type: {period_type}')
            if v not in valid_frequency_type:
                raise ValueError(f'Invalid frequency_type for period_type {period_type}, must be one of: {valid_frequency_type}')

        return v

    @field_validator('frequency')
    def validate_frequency(cls, v, info):
        if 'frequency_type' in info.data:
            valid_frequencies = {
                'minute': [1, 5, 10, 15, 30],
                'daily': [1],
                'weekly': [1],
                'monthly': [1]
            }
            frequency_type = info.data['frequency_type']
            valid_frequency = valid_frequencies.get(frequency_type, None)
            if not valid_frequency:
                raise ValueError(f'Invalid frequency type: {frequency_type}')
            if v not in valid_frequency:
                raise ValueError(f'Invalid frequency for frequency_type {frequency_type}, must be one of: {valid_frequency}')
        return v
