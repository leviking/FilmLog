ALTER TABLE Prints
  ADD COLUMN exposureTimeNew SMALLINT UNSIGNED;
UPDATE Prints SET exposureTimeNew = TIME_TO_SEC(exposureTime);
ALTER TABLE Prints DROP COLUMN exposureTime;
ALTER TABLE Prints CHANGE COLUMN exposureTimeNew exposureTime SMALLINT UNSIGNED;
