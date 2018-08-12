CREATE TABLE Developers(
    developerID TINYINT UNSIGNED NOT NULL,
    name VARCHAR(64)
) ENGINE='InnoDB';

CREATE TABLE Recipes(
    userID INT UNSIGNED NOT NULL,
    recipeID SMALLINT UNSIGNED NOT NULL,
    developerID TINYINT UNSIGNED NOT NULL,
    duration SMALLINT UNSIGNED,
    method ENUM('Inversion', 'Rotary', 'Stand', 'Semi-Stand'),
    temperature TINYINT UNSIGNED,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, recipeID)
) ENGINE='InnoDB';
