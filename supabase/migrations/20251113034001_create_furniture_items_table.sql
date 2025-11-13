/*
  # Create furniture items table

  1. New Tables
    - `furniture_items`
      - `id` (uuid, primary key) - Unique identifier for each furniture item
      - `user_id` (uuid, nullable) - Reference to user who uploaded (null for guest uploads)
      - `name` (text) - Name/description of the furniture item
      - `category` (text) - Category like 'sofa', 'table', 'lamp', 'painting', 'chair', etc.
      - `image_url` (text) - URL to the stored image in Supabase Storage
      - `created_at` (timestamptz) - Timestamp when uploaded
      - `updated_at` (timestamptz) - Timestamp when last modified
  
  2. Security
    - Enable RLS on `furniture_items` table
    - Add policy for users to read all furniture items
    - Add policy for authenticated users to insert their own items
    - Add policy for authenticated users to update their own items
    - Add policy for authenticated users to delete their own items
    - Add policy for guests to insert items (with null user_id)
  
  3. Indexes
    - Add index on user_id for faster queries
    - Add index on category for filtering
*/

CREATE TABLE IF NOT EXISTS furniture_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  name text NOT NULL,
  category text NOT NULL,
  image_url text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE furniture_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view furniture items"
  ON furniture_items FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can insert their own furniture"
  ON furniture_items FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Guests can insert furniture with null user_id"
  ON furniture_items FOR INSERT
  TO anon
  WITH CHECK (user_id IS NULL);

CREATE POLICY "Users can update their own furniture"
  ON furniture_items FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own furniture"
  ON furniture_items FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_furniture_user_id ON furniture_items(user_id);
CREATE INDEX IF NOT EXISTS idx_furniture_category ON furniture_items(category);