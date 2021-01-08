ALTER TABLE Cameras
    MODIFY COLUMN filmSize ENUM('35mm', '120', '220', '4x5', '5x7', '8x10') NOT NULL;
