
ALTER TABLE LensShutterSpeeds
MODIFY COLUMN `differenceStops` float GENERATED ALWAYS AS
((ROUND(LOG2(idealSpeedMicroseconds / measuredSpeedMicroseconds),2)) * -1)
VIRTUAL,
DROP COLUMN differencePercent;   
