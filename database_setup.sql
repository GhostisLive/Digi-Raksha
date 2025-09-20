-- Supabase SQL script to create tables for Digi-रक्षा application

-- Users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    last_name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    gov_id_type VARCHAR(50) NOT NULL,
    gov_id_number VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Incidents table
CREATE TABLE incidents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    incident_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    location TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    photo_url TEXT,
    status VARCHAR(20) DEFAULT 'reported',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Missing persons table
CREATE TABLE missing_persons (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    last_seen_location TEXT NOT NULL,
    description TEXT NOT NULL,
    reporter_contact VARCHAR(255) NOT NULL,
    photo_url TEXT,
    status VARCHAR(20) DEFAULT 'missing',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Community posts table
CREATE TABLE community_posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    location TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SOS alerts table
CREATE TABLE sos_alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location_description TEXT,
    emergency_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Safe status table (for tracking when users mark themselves as safe)
CREATE TABLE safe_status (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    message TEXT DEFAULT 'User marked as safe',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_incidents_user_id ON incidents(user_id);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);
CREATE INDEX idx_missing_persons_user_id ON missing_persons(user_id);
CREATE INDEX idx_missing_persons_status ON missing_persons(status);
CREATE INDEX idx_community_posts_user_id ON community_posts(user_id);
CREATE INDEX idx_community_posts_category ON community_posts(category);
CREATE INDEX idx_sos_alerts_user_id ON sos_alerts(user_id);
CREATE INDEX idx_sos_alerts_status ON sos_alerts(status);
CREATE INDEX idx_safe_status_user_id ON safe_status(user_id);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE missing_persons ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sos_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE safe_status ENABLE ROW LEVEL SECURITY;

-- Basic policies (you may want to customize these based on your requirements)
-- Users can read their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

-- Users can update their own data
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- All authenticated users can read incidents
CREATE POLICY "All users can view incidents" ON incidents
    FOR SELECT USING (true);

-- Users can create incidents
CREATE POLICY "Users can create incidents" ON incidents
    FOR INSERT WITH CHECK (true);

-- Similar policies for other tables...
CREATE POLICY "All users can view missing persons" ON missing_persons
    FOR SELECT USING (true);

CREATE POLICY "Users can report missing persons" ON missing_persons
    FOR INSERT WITH CHECK (true);

CREATE POLICY "All users can view community posts" ON community_posts
    FOR SELECT USING (true);

CREATE POLICY "Users can create community posts" ON community_posts
    FOR INSERT WITH CHECK (true);

CREATE POLICY "All users can view SOS alerts" ON sos_alerts
    FOR SELECT USING (true);

CREATE POLICY "Users can create SOS alerts" ON sos_alerts
    FOR INSERT WITH CHECK (true);

CREATE POLICY "All users can view safe status" ON safe_status
    FOR SELECT USING (true);

CREATE POLICY "Users can create safe status" ON safe_status
    FOR INSERT WITH CHECK (true);