DROP TABLE LensShutterSpeeds;
CREATE TABLE LensShutterSpeeds(
    userID INT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    speed SMALLINT UNSIGNED NOT NULL,
    idealSpeedMicroseconds INT UNSIGNED AS ((1/speed) * 1000000) VIRTUAL,
    measuredSpeedMicroseconds INT UNSIGNED NOT NULL,
    differencePercent SMALLINT AS ((1/((1/speed * 1000000) / measuredSpeedMicroseconds)) * 100) VIRTUAL,
    differenceStops FLOAT AS ((((1/((1/speed * 1000000) / measuredSpeedMicroseconds)) * 100) / 100) - 1) VIRTUAL,
    PRIMARY KEY (userID, lensID, speed),
    CONSTRAINT LensShutterSpeeds_Lenses FOREIGN KEY (userID, lensID) REFERENCES Lenses
        (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';
