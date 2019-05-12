
ALTER TABLE LensShutterSpeeds
MODIFY COLUMN `differenceStops` float GENERATED ALWAYS AS
((ROUND(LOG2((1 / speed * 1000000) / measuredSpeedMicroseconds),2)) * -1)
VIRTUAL,
DROP COLUMN differencePercent;
