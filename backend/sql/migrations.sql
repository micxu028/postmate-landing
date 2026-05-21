-- PostMate Database Schema
-- Run this in Supabase SQL Editor

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);
CREATE INDEX idx_users_email ON users(email);

-- Brands
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    industry TEXT NOT NULL CHECK (industry IN ('yoga', 'fitness', 'pilates')),
    style TEXT NOT NULL CHECK (style IN ('professional', 'warm', 'energetic', 'minimalist')),
    tone TEXT NOT NULL CHECK (tone IN ('professional', 'friendly', 'humorous', 'inspirational')),
    post_frequency INT DEFAULT 7 CHECK (post_frequency IN (3, 5, 7)),
    city TEXT,
    state TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_brands_user ON brands(user_id);

-- Brand images
CREATE TABLE brand_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_brand_images_brand ON brand_images(brand_id);

-- Posts
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE NOT NULL,
    week_start DATE NOT NULL,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    caption TEXT NOT NULL,
    hashtags TEXT[] DEFAULT '{}',
    image_url TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'generating')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ
);
CREATE INDEX idx_posts_brand_week ON posts(brand_id, week_start);

-- Generation logs
CREATE TABLE generation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('text', 'image')),
    status TEXT NOT NULL CHECK (status IN ('success', 'failed')),
    prompt TEXT,
    response TEXT,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
