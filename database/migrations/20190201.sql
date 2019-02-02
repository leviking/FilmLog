RENAME TABLE ShutterSpeeds TO LensShutterSpeeds;
ALTER TABLE LensShutterSpeeds DROP FOREIGN KEY ShutterSpeeds_Lenses;
ALTER TABLE LensShutterSpeeds ADD CONSTRAINT LensShutterSpeeds_Lenses
  FOREIGN KEY (`userID`, `lensID`) REFERENCES `Lenses` (`userID`, `lensID`) ON UPDATE CASCADE;

ALTER TABLE Lenses ADD COLUMN shutter ENUM ('Yes', 'No') DEFAULT 'No';

ALTER TABLE LensShutterSpeeds
MODIFY COLUMN differencePercent SMALLINT AS ((1/((1/speed * 1000) / measuredSpeedMS)) * 100) VIRTUAL,
MODIFY COLUMN differenceStops FLOAT AS ((((1/((1/speed * 1000) / measuredSpeedMS)) * 100) / 100) - 1) VIRTUAL;
