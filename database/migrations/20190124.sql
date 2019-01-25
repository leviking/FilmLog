CREATE TABLE ShutterSpeeds(
    userID INT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    speed SMALLINT UNSIGNED NOT NULL,
    idealSpeedMS SMALLINT UNSIGNED AS ((1/speed) * 1000) VIRTUAL,
    measuredSpeedMS SMALLINT UNSIGNED NOT NULL,
    differencePercent SMALLINT UNSIGNED AS ((1/((1/speed * 1000) / measuredSpeedMS)) * 100) VIRTUAL,
    differenceStops DECIMAL(4,2) UNSIGNED AS ((((1/((1/speed * 1000) / measuredSpeedMS)) * 100) / 100) - 1) VIRTUAL,
    PRIMARY KEY (userID, lensID, speed),
    CONSTRAINT ShutterSpeeds_Lenses FOREIGN KEY (userID, lensID) REFERENCES Lenses
        (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';
