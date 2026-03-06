-- 1. Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- 2. Create the users table
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz default now(),
  face_embedding vector(512), -- Matches our InsightFace/Buffalo_L model dimension
  image_url text,
  status text default 'active',
  last_verified_at timestamptz,
  confidence_score float -- Optional, for logs if needed
);

-- 3. Create a function to search for similar faces
-- We use Cosine Similarity (1 - cosine distance)
-- The operator <=> is cosine distance
create or replace function match_faces (
  query_embedding vector(512),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  name text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    users.id,
    users.name,
    1 - (users.face_embedding <=> query_embedding) as similarity
  from users
  where 1 - (users.face_embedding <=> query_embedding) > match_threshold
  order by users.face_embedding <=> query_embedding
  limit match_count;
end;
$$;

-- 4. Create a storage bucket for images (You also need to do this in the UI, but this is the name we expect)
-- Bucket Name: "biometric_images"
-- Ensure Policy: "Public" or Signed URL access.
