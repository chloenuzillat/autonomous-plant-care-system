# Data

For simplicity we will only be working with SI Units while working on sensor related data.

## Tables

- **`plant_info`** - **global** species reference data, sourced from a GlobalAPI: 
  the light, temperature and humidity ranges every plant of that species
  wants. It is not about any one houseplant, so it carries no position and no
  readings. All ten species stay stocked in `mock_data/mock_plant_info.csv`
  regardless of how many plants the user owns.
- **`user_plant_log`** - **local** measured data: what the robot actually
  recorded in this user's home. Information such as species, ideal lux, humidity, soil moisture
  and temperature might be used to improve the global dataset and model training.

The two are compared to judge whether a spot suits a plant: readings from
`user_plant_log` against the ranges in `plant_info`.

## The two ids

A reading carries both, because the user can own several plants of the same
species:

- `user_plant_id` - which individual pot the reading came from. Readings are
  grouped, queried and deleted by this.
- `plant_id` - what species that pot is, and the key `plant_info` is keyed by.

Where an individual plant stands is a property of that plant, not of its
species — see `simulation/plant.py`.

## Ambient vs. pot readings

`lux_reading`, `temp_reading` and `humidity_reading` are **ambient**: they
describe the spot, so any plant standing there would read the same. These drive
placement decisions.

`soil_moisture_pct` is **NOT**: it describes the inside of one pot and mostly
reflects when that plant was last watered. It drives watering decisions, and
should be kept out of placement scoring otherwise a good spot looks bad just
because you watered late. The signal that does connect the two is the drying
rate, which depends on the ambient conditions at that spot.

## Positions

`pos_x`, `pos_y` and `heading_deg` record where the robot stood when it took the
reading, measured to the centre of the robot, with 0 degrees facing +x and 90
facing up.

The store does not check whether a pose is reachable that belongs to the robot
that produced it, so this module runs unchanged against the simulation or a real
robot. Today's coordinates come from the simulated floor plan in
`simulation/config.py` (800 x 600, origin top-left, y growing downward).

## Mock layout

`mock_data/mock_user_plant_log.csv` assumes a user with **two** plants:

| user_plant_id | plant_id | species     | pot stands at | robot parks near |
| ------------- | -------- | ----------- | ------------- | ---------------- |
| 1             | 1        | Snake Plant | (80, 80)      | (130, 130)       |
| 2             | 7        | Sweet Basil | (740, 540)    | (690, 490)       |

Both spots are clear of the two obstacles in `simulation/config.py`
