ALTER TABLE FilmTests
ADD COLUMN graph ENUM('Yes', 'No') DEFAULT 'No' AFTER expLog;

CREATE VIEW FilmTestsView AS
SELECT FilmTests.filmTestID, FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
filmSize, developer, SEC_TO_TIME(devTime) AS devTime, Filters.code AS filter,
lux, fstop,
gamma, contrastIndex, kodakISO
FROM FilmTests
JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
    AND FilmTypes.filmTypeID = FilmTests.filmTypeID
JOIN Filters ON Filters.userID = FilmTests.userID
    AND Filters.filterID = FilmTests.filterID
ORDER BY filmName, filmISO, devTime;
