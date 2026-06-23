BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> d84b6248dcfa

CREATE TABLE clients (
    client_id SERIAL NOT NULL, 
    email VARCHAR(50) NOT NULL, 
    first_name VARCHAR(50) NOT NULL, 
    last_name VARCHAR(50) NOT NULL, 
    phone VARCHAR(12) NOT NULL, 
    unsubscribe_token VARCHAR(64) NOT NULL, 
    subscribed BOOLEAN NOT NULL, 
    PRIMARY KEY (client_id), 
    CONSTRAINT max_email_length CHECK (length(email) <= 50), 
    CONSTRAINT min_email_length CHECK (length(email) >= 5), 
    CONSTRAINT max_first_name_length CHECK (length(first_name) <= 50), 
    CONSTRAINT min_first_name_length CHECK (length(first_name) >= 1), 
    CONSTRAINT max_last_name_length CHECK (length(last_name) <= 50), 
    CONSTRAINT min_last_name_length CHECK (length(last_name) >= 1), 
    CONSTRAINT phone_size CHECK (length(phone) = 12), 
    UNIQUE (email), 
    UNIQUE (unsubscribe_token)
);

CREATE TABLE errors (
    error_id SERIAL NOT NULL, 
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    message VARCHAR NOT NULL, 
    stack_trace TEXT, 
    PRIMARY KEY (error_id)
);

CREATE TABLE bookings (
    booking_id SERIAL NOT NULL, 
    client_id INTEGER NOT NULL, 
    service VARCHAR(30) NOT NULL, 
    type VARCHAR(100) NOT NULL, 
    company VARCHAR(100), 
    company_age VARCHAR(20), 
    business_revenue VARCHAR(20), 
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    additional_info VARCHAR, 
    meet_link VARCHAR, 
    PRIMARY KEY (booking_id), 
    CONSTRAINT valid_service CHECK (service IN ('tax', 'accounting', 'business consulting', 'other')), 
    CONSTRAINT valid_type CHECK (type IN ('personal', 'business', 'both')), 
    CONSTRAINT valid_date CHECK (date >= NOW()), 
    CONSTRAINT max_business_revenue_length CHECK (length(business_revenue) <= 20), 
    CONSTRAINT min_business_revenue_length CHECK (length(business_revenue) >= 1), 
    CONSTRAINT max_company_length CHECK (length(company) <= 100), 
    CONSTRAINT min_company_length CHECK (length(company) >= 1), 
    CONSTRAINT max_company_age_length CHECK (length(company_age) <= 20), 
    CONSTRAINT min_company_age_length CHECK (length(company_age) >= 1), 
    CONSTRAINT max_service_length CHECK (length(service) <= 30), 
    CONSTRAINT min_service_length CHECK (length(service) >= 1), 
    CONSTRAINT max_type_length CHECK (length(type) <= 100), 
    CONSTRAINT min_type_length CHECK (length(type) >= 1), 
    FOREIGN KEY(client_id) REFERENCES clients (client_id) ON DELETE CASCADE
);

INSERT INTO alembic_version (version_num) VALUES ('d84b6248dcfa') RETURNING alembic_version.version_num;

-- Running upgrade d84b6248dcfa -> 3a2a6ab636fe

ALTER TABLE bookings ADD COLUMN reminders_sent VARCHAR(100);

UPDATE alembic_version SET version_num='3a2a6ab636fe' WHERE alembic_version.version_num = 'd84b6248dcfa';

COMMIT;

