ALTER TABLE FilmTests
  ADD COLUMN developer VARCHAR(32) NOT NULL AFTER expLog,
  ADD COLUMN devTime SMALLINT UNSIGNED NOT NULL AFTER exposureTime,
  ADD COLUMN devTemperature DECIMAL(3,1) UNSIGNED NOT NULL AFTER devTime,
  ADD COLUMN prebath ENUM('No', 'Water') NOT NULL DEFAULT 'No' AFTER devTemperature,
  ADD COLUMN stop ENUM('Stop Bath', 'Water') NOT NULL DEFAULT 'Stop Bath' AFTER prebath,
  ADD COLUMN agitation ENUM('Rotary', 'Hand-Inversions', 'Dip and Dunk', 'Tray') NOT NULL DEFAULT 'Hand-Inversions' AFTER stop,
  ADD COLUMN rotaryRPM TINYINT UNSIGNED DEFAULT NULL AFTER agitation;

UPDATE FilmTests
JOIN DevRecipes ON DevRecipes.userID = FilmTests.userID
AND DevRecipes.devRecipeID = FilmTests.devRecipeID
SET FilmTests.developer = DevRecipes.developer,
FilmTests.devTime = DevRecipes.time,
FilmTests.devTemperature = DevRecipes.temperature,
FilmTests.prebath = DevRecipes.prebath,
FilmTests.stop = DevRecipes.stop,
FilmTests.agitation = DevRecipes.agitation,
FilmTests.rotaryRPM = DevRecipes.rotaryRPM;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE DevRecipes;
ALTER TABLE FilmTests
DROP FOREIGN KEY FilmTests_DevRecipes_fk,
DROP COLUMN devRecipeID;

SET FOREIGN_KEY_CHECKS=1;
