/*
  # Create room_designs table for storing generated AI designs

  1. New Tables
    - `room_designs`
      - `id` (uuid, primary key)
      - `user_id` (uuid, nullable - for future auth integration)
      - `original_image_url` (text) - URL to original room image uploaded by user
      - `generated_image_url` (text) - URL to AI-generated design image
      - `design_type` (text) - interior/exterior
      - `room_type` (text) - living/bedroom/kitchen/etc
      - `style` (text) - modern/rustic/bohemian/etc
      - `background_color` (text) - hex color
      - `foreground_color` (text) - hex color
      - `instructions` (text, nullable) - user instructions
      - `description` (text, nullable) - AI-generated description
      - `created_at` (timestamptz)
  
  2. Security
    - Enable RLS on `room_designs` table
    - Add policy for public read access (for testing)
    - Add policy for public insert access (for testing)
    - Note: In production, these should be restricted to authenticated users
*/

CREATE TABLE IF NOT EXISTS room_designs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  original_image_url text NOT NULL,
  generated_image_url text NOT NULL,
  design_type text NOT NULL,
  room_type text NOT NULL,
  style text NOT NULL,
  background_color text DEFAULT '#ffffff',
  foreground_color text DEFAULT '#000000',
  instructions text,
  description text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE room_designs ENABLE ROW LEVEL SECURITY;

-- For testing purposes, allow public access
-- In production, replace with proper user-based policies
CREATE POLICY "Allow public read access for testing"
  ON room_designs
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public insert for testing"
  ON room_designs
  FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "Allow public update for testing"
  ON room_designs
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete for testing"
  ON room_designs
  FOR DELETE
  TO public
  USING (true);