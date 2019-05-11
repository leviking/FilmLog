ALTER TABLE LensShutterSpeeds
ADD COLUMN measuredSpeed SMALLINT AS (1/(measuredSpeedMicroseconds / 1000000)) VIRTUAL AFTER speed;
