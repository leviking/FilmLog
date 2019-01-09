ALTER TABLE Cameras
  ADD COLUMN status ENUM('Active', 'Inactive') DEFAULT 'Active' AFTER filmSize;
