CREATE TABLE CameraShutterSpeeds(
    userID INT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED NOT NULL,
    speed SMALLINT UNSIGNED NOT NULL,
    measuredSpeed SMALLINT AS (1/(measuredSpeedMicroseconds / 1000000)) VIRTUAL,
    idealSpeedMicroseconds INT UNSIGNED AS ((1/speed) * 1000000) VIRTUAL,
    measuredSpeedMicroseconds INT UNSIGNED NOT NULL,
    differenceStops FLOAT GENERATED ALWAYS AS ((ROUND(LOG2((1 / speed * 1000000) / measuredSpeedMicroseconds),2)) * -1),
    PRIMARY KEY (userID, cameraID, speed),
    CONSTRAINT CameraShutterSpeeds_Cameras FOREIGN KEY (userID, cameraID) REFERENCES Cameras
        (userID, cameraID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

ALTER TABLE Cameras
  ADD COLUMN integratedShutter ENUM('Yes', 'No') DEFAULT 'No'
  AFTER filmSize;
