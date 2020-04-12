ALTER TABLE Papers
  ADD UNIQUE user_name (userID, name);

ALTER TABLE Cameras
  ADD COLUMN notes TEXT DEFAULT NULL AFTER name; 
