# Data Contract

## Required columns

| Column | Type | Rule |
|---|---|---|
| `timestamp` | timezone-aware datetime | unique and sorted ascending |
| `open` | finite float | greater than zero |
| `high` | finite float | greater than or equal to open, close, and low |
| `low` | finite float | less than or equal to open, close, and high |
| `close` | finite float | greater than zero |
| `volume` | finite float | greater than or equal to zero |

## CSV example

```csv
timestamp,open,high,low,close,volume
2024-01-01T00:00:00Z,100.0,101.2,99.5,100.8,1200
2024-01-01T01:00:00Z,100.8,102.0,100.1,101.5,1250
```

## Validation philosophy

The validator fails early rather than silently repairing ambiguous data. Resampling is a separate explicit transformation, which makes frequency changes reviewable and testable.
