from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import traceback
import base64
from config.supabase_client import supabase
import requests

load_dotenv()

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

@router.post("/furniture-placement")
async def place_furniture(
    room_design_id: str = Form(...),
    furniture_images: list[UploadFile] = File(...),
):
    try:
        MAX_IMAGE_SIZE_MB = 10
        ALLOWED_MIME_TYPES = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/heic",
            "image/heif",
        }

        # Fetch the room design from database
        room_design_response = supabase.table("room_designs").select("*").eq("id", room_design_id).maybeSingle().execute()

        if not room_design_response.data:
            raise HTTPException(status_code=404, detail="Room design not found")

        room_design = room_design_response.data

        # Fetch the generated room image
        try:
            room_image_response = requests.get(room_design["generated_image_url"], timeout=10)
            if room_image_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch room design image")
            room_image_bytes = room_image_response.content
        except Exception as fetch_err:
            print(f"Failed to fetch room image: {fetch_err}")
            raise HTTPException(status_code=500, detail="Failed to fetch room design image")

        # Process furniture images
        furniture_parts = []
        furniture_descriptions = []

        for idx, furniture_img in enumerate(furniture_images):
            if furniture_img.content_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for furniture image {idx + 1}: {furniture_img.content_type}"
                )

            furniture_bytes = await furniture_img.read()
            size_in_mb = len(furniture_bytes) / (1024 * 1024)

            if size_in_mb > MAX_IMAGE_SIZE_MB:
                raise HTTPException(
                    status_code=400,
                    detail=f"Furniture image {idx + 1} exceeds 10MB size limit"
                )

            furniture_parts.append(
                types.Part.from_bytes(
                    data=furniture_bytes,
                    mime_type=furniture_img.content_type,
                )
            )
            furniture_descriptions.append(f"Furniture item {idx + 1}")

        # Build prompt for AI
        prompt = f"""
        You are a professional AI interior designer specialized in furniture placement.

        ### Task:
        You are provided with:
        1. A room design image (the base room)
        2. {len(furniture_images)} furniture/object image(s) that need to be placed in this room

        ### Room Context:
        - Design Type: {room_design['design_type']}
        - Room Type: {room_design['room_type']}
        - Style: {room_design['style']}

        ### Objective:
        1. Naturally integrate ALL the provided furniture/object images into the room design
        2. Place each furniture item in an appropriate location based on its type and the room layout
        3. Ensure proper scaling so furniture looks proportional to the room
        4. Maintain realistic perspective and shadows
        5. Make sure the furniture blends seamlessly with the existing design aesthetic
        6. Consider practical placement (e.g., sofa against wall, table in center, lamps near seating)
        7. Preserve the original room's lighting, colors, and overall atmosphere

        ### Important:
        - The furniture should look like it naturally belongs in the room
        - Maintain photorealistic quality
        - Don't change the room structure, only add the furniture
        - Ensure proper depth perception and spatial relationships

        Return:
        - A photorealistic image of the room WITH all the furniture items placed naturally
        - A brief description of where each piece was placed and why
        """

        print(prompt)

        # Build content parts for Gemini
        contents = [
            prompt,
            types.Part.from_bytes(
                data=room_image_bytes,
                mime_type="image/jpeg",
            )
        ]

        contents.extend(furniture_parts)

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        print(response)

        # Extract image and text from response
        image_data = None
        text_response = "No description available."

        if response.candidates and len(response.candidates) > 0:
            parts = response.candidates[0].content.parts

            if parts:
                print("Number of parts in response:", len(parts))

                for part in parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        image_data = part.inline_data.data
                        image_mime_type = getattr(part.inline_data, "mime_type", "image/png")
                        print("Image data received, length:", len(image_data))
                        print("MIME type:", image_mime_type)

                    elif hasattr(part, "text") and part.text:
                        text_response = part.text
                        preview = (text_response[:100] + "...") if len(text_response) > 100 else text_response
                        print("Text response received:", preview)
            else:
                print("No parts found in the response candidate.")
        else:
            print("No candidates found in the API response.")

        image_url = None
        if image_data:
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            image_url = f"data:{image_mime_type};base64,{image_base64}"
        else:
            image_url = None

        return JSONResponse(
            content={
                "image": image_url,
                "text": text_response,
                "room_design_id": room_design_id
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /api/furniture-placement endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
