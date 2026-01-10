-- OpenIMIS Legacy Tables Creation Script
-- This script creates the minimal legacy tables required for migrations to work
-- Run this BEFORE python manage.py migrate

-- ============================================================
-- tblUsers (InteractiveUser)
-- ============================================================
CREATE TABLE IF NOT EXISTS "tblUsers" (
    "UserID" SERIAL PRIMARY KEY,
    "LoginName" VARCHAR(25) NOT NULL UNIQUE,
    "PrivateKey" VARCHAR(256),
    "StoredPassword" VARCHAR(256),
    "EmailId" VARCHAR(200),
    "HealthFacilityId" INTEGER,
    "RoleID" INTEGER,
    "LanguageID" VARCHAR(1) DEFAULT 'en',
    "LastName" VARCHAR(100) NOT NULL,
    "OtherNames" VARCHAR(100) NOT NULL,
    "Phone" VARCHAR(50),
    "ValidityFrom" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ValidityTo" TIMESTAMP,
    "LegacyId" INTEGER,
    "AuditUserId" INTEGER
);

-- ============================================================
-- tblLanguages
-- ============================================================
CREATE TABLE IF NOT EXISTS "tblLanguages" (
    "LanguageCode" VARCHAR(5) PRIMARY KEY,
    "LanguageName" VARCHAR(50) NOT NULL,
    "SortOrder" INTEGER
);

-- Insert default language
INSERT INTO "tblLanguages" ("LanguageCode", "LanguageName", "SortOrder")
VALUES ('en', 'English', 1)
ON CONFLICT ("LanguageCode") DO NOTHING;

-- ============================================================
-- tblRole
-- ============================================================
CREATE TABLE IF NOT EXISTS "tblRole" (
    "RoleID" SERIAL PRIMARY KEY,
    "RoleName" VARCHAR(50) NOT NULL,
    "AltLanguage" VARCHAR(50),
    "IsSystem" SMALLINT DEFAULT 0,
    "IsBlocked" SMALLINT DEFAULT 0,
    "ValidityFrom" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ValidityTo" TIMESTAMP,
    "LegacyId" INTEGER,
    "AuditUserId" INTEGER
);

-- ============================================================
-- tblRoleRight
-- ============================================================
CREATE TABLE IF NOT EXISTS "tblRoleRight" (
    "RoleRightID" SERIAL PRIMARY KEY,
    "RoleID" INTEGER NOT NULL,
    "RightID" INTEGER NOT NULL,
    "ValidityFrom" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ValidityTo" TIMESTAMP,
    "LegacyId" INTEGER,
    "AuditUserId" INTEGER
);

-- ============================================================
-- tblUserRole
-- ============================================================
CREATE TABLE IF NOT EXISTS "tblUserRole" (
    "UserRoleID" SERIAL PRIMARY KEY,
    "UserID" INTEGER NOT NULL,
    "RoleID" INTEGER NOT NULL,
    "ValidityFrom" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ValidityTo" TIMESTAMP,
    "LegacyId" INTEGER,
    "AuditUserId" INTEGER
);

-- ============================================================
-- tblOfficer
-- ============================================================
CREATE TABLE IF NOT EXISTS "tblOfficer" (
    "OfficerID" SERIAL PRIMARY KEY,
    "Code" VARCHAR(8) NOT NULL UNIQUE,
    "LastName" VARCHAR(100) NOT NULL,
    "OtherNames" VARCHAR(100) NOT NULL,
    "Phone" VARCHAR(25),
    "LocationId" INTEGER,
    "OfficerIDSubst" INTEGER,
    "WorksTo" DATE,
    "VEOCode" VARCHAR(8),
    "VEOLastName" VARCHAR(100),
    "VEOOtherNames" VARCHAR(100),
    "VEOPhone" VARCHAR(25),
    "VEODob" DATE,
    "EmailId" VARCHAR(200),
    "PermanentAddress" VARCHAR(200),
    "HasLogin" SMALLINT DEFAULT 0,
    "ValidityFrom" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ValidityTo" TIMESTAMP,
    "LegacyId" INTEGER,
    "AuditUserId" INTEGER
);

-- ============================================================
-- tblClaimAdmin
-- ============================================================
CREATE TABLE IF NOT EXISTS "tblClaimAdmin" (
    "ClaimAdminId" SERIAL PRIMARY KEY,
    "ClaimAdminCode" VARCHAR(8) NOT NULL UNIQUE,
    "LastName" VARCHAR(100) NOT NULL,
    "OtherNames" VARCHAR(100) NOT NULL,
    "DOB" DATE,
    "Phone" VARCHAR(50),
    "EmailId" VARCHAR(200),
    "HFId" INTEGER,
    "HasLogin" SMALLINT DEFAULT 0,
    "ValidityFrom" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ValidityTo" TIMESTAMP,
    "LegacyId" INTEGER,
    "AuditUserId" INTEGER
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_tblUsers_LoginName ON "tblUsers"("LoginName");
CREATE INDEX IF NOT EXISTS idx_tblUsers_RoleID ON "tblUsers"("RoleID");
CREATE INDEX IF NOT EXISTS idx_tblRoleRight_RoleID ON "tblRoleRight"("RoleID");
CREATE INDEX IF NOT EXISTS idx_tblUserRole_UserID ON "tblUserRole"("UserID");
CREATE INDEX IF NOT EXISTS idx_tblUserRole_RoleID ON "tblUserRole"("RoleID");

-- ============================================================
-- Default Admin User (password: admin)
-- ============================================================
INSERT INTO "tblUsers" (
    "LoginName",
    "LastName",
    "OtherNames",
    "EmailId",
    "StoredPassword",
    "ValidityFrom"
)
VALUES (
    'admin',
    'Administrator',
    'System',
    'admin@openimis.org',
    'pbkdf2_sha256$260000$xyz$hash',  -- Change this in production!
    NOW()
)
ON CONFLICT ("LoginName") DO NOTHING;

COMMIT;
