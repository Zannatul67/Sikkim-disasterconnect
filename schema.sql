-- Sikkim disaster events, 1985-2026 (30 events; see notes before using for any analysis)
CREATE TABLE IF NOT EXISTS disaster_events (
  event_id INTEGER PRIMARY KEY,
  date_text TEXT,            -- as given in sources (some are month/year only)
  year INTEGER NOT NULL,
  event TEXT NOT NULL,
  hazard_type TEXT NOT NULL, -- Landslide | Earthquake | GLOF / Flash flood | Avalanche | Snowfall / stranding
  location_text TEXT,
  district_primary TEXT,     -- Gangtok | Pakyong | Mangan | Namchi | Soreng | Gyalshing | Statewide | Multiple | Unknown
  districts_other TEXT,
  district_basis TEXT,       -- location in source | inferred from place name | not stated in source
  deaths INTEGER,            -- NULL = not stated, not zero
  missing INTEGER,
  people_affected INTEGER,
  notes TEXT,
  source TEXT
);
CREATE VIEW IF NOT EXISTS district_summary AS
SELECT district_primary AS district,
       COUNT(*) AS events,
       SUM(deaths) AS deaths_reported,
       SUM(missing) AS missing_reported,
       SUM(people_affected) AS people_affected
FROM disaster_events GROUP BY district_primary ORDER BY events DESC;
