ALTER TABLE FilmTests
  MODIFY COLUMN exposureTime DECIMAL(4,2) UNSIGNED NOT NULL;
UPDATE FilmTests SET exposureTime = 1/exposureTime;
DROP VIEW FilmTestStepsView;
CREATE VIEW FilmTestStepsView AS
SELECT FilmTestSteps.userID, FilmTestSteps.filmTestID, FilmTestSteps.stepNumber, stepDensity,
ROUND(LOG10(lux * exposureTime * 1000) - stepDensity, 2) AS logE, filmDensity
FROM FilmTestSteps
JOIN FilmTests ON FilmTests.filmTestID = FilmTestSteps.filmTestID
    AND FilmTests.userID = FilmTestSteps.userID
JOIN StepTablets ON StepTablets.stepTabletID = FilmTests.stepTabletID
    AND StepTablets.userID = FilmTests.userID
JOIN StepTabletSteps ON StepTabletSteps.stepTabletID = StepTablets.stepTabletID
    AND StepTabletSteps.userID = StepTablets.userID
    AND StepTabletSteps.stepNumber = FilmTestSteps.stepNumber;
