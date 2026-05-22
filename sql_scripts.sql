-- CREATE TABLE mhtest (
--     id INT PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP
-- );

INSERT INTO dbo.mhtest (id, name) VALUES (2, 'Other Name');

SELECT * FROM dbo.mhtest;


CREATE TABLE dbo.Logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    person_id INT,  
    role NVARCHAR(50),
    message NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE()
);

DROP TABLE dbo.Logs