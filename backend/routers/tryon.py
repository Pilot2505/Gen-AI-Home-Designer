from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from utils.base64_helpers import array_buffer_to_base64
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import traceback
import base64
from typing import List
from config.supabase_client import supabase
import requests
import uuid

load_dotenv()

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

@router.post("/try-on")
async def try_on(
    place_image: UploadFile = File(...),
    design_type: str = Form(...),
    room_type: str = Form(...),
    style: str = Form(...),
    background_color: str = Form(...),
    foreground_color: str = Form(...),
    instructions: str = Form(""),
    furniture_ids: str = Form(""),

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

        if place_image.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400, detail=f"Unsupported file type for place_image: {place_image.content_type}"
            )

        place_bytes = await place_image.read()

        size_in_mb_for_place_image = len(place_bytes) / (1024 * 1024)
        if size_in_mb_for_place_image > MAX_IMAGE_SIZE_MB:
            raise HTTPException(status_code=400, detail="Image exceeds 10MB size limit for place_image")


        place_b64 = array_buffer_to_base64(place_bytes)

        furniture_info = ""
        furniture_parts = []

        if furniture_ids:
            ids_list = [fid.strip() for fid in furniture_ids.split(",") if fid.strip()]

            if ids_list:
                furniture_response = supabase.table("furniture_items").select("*").in_("id", ids_list).execute()

                if furniture_response.data:
                    furniture_info = "\n\n### User's Furniture to Include:\n"

                    for idx, furniture in enumerate(furniture_response.data):
                        furniture_info += f"{idx + 1}. **{furniture['name']}** (Category: {furniture['category']})\n"

                        try:
                            img_response = requests.get(furniture['image_url'], timeout=10)
                            if img_response.status_code == 200:
                                furniture_parts.append(
                                    types.Part.from_bytes(
                                        data=img_response.content,
                                        mime_type="image/jpeg"
                                    )
                                )
                        except Exception as img_err:
                            print(f"Failed to fetch furniture image: {img_err}")

        prompt = f"""
        You are a professional AI interior and exterior designer.
        Your task is to redesign a user's uploaded space.

        ### User Input
        - **Design Type:** {design_type}
        - **Room Type:** {room_type}
        - **Style:** {style}
        - **Background Color Preference:** {background_color}
        - **Foreground Color Preference:** {foreground_color}
        - **Instructions:** {instructions}
        {furniture_info}

        ### Objective:
        1. Apply the chosen design style (e.g., {style}) to the uploaded {room_type}.
        2. Enhance the space visually while respecting the structure of the original layout.
        3. Harmonize background/foreground color preferences subtly in the decor.
        4. Produce a **photo-realistic redesign image** and a **short textual description**.
        5. You don't need change any structure of the room, just the design.
        6. The design should be realistic and practical for the user.
        7. The design should be aligned with the user's preferences and instructions.
        8. Also return the cost and time required for the redesign.
        9. Return the cost of design and the the in depth description of the design.
        10. Return all colors of the design in hex format.
        11. Return cost of the design in USD.
        12. **IMPORTANT**: If user furniture images are provided, naturally integrate them into the redesigned space. Place them appropriately based on their category and the room layout. Make sure they blend seamlessly with the overall design aesthetic.

        Return:
        - A realistic redesigned image of the space.
        - A short caption describing the redesign, highlighting how it aligns with the selected preferences and suggesting improvements.
        """
               
   
        
        print(prompt)

        contents=[
            prompt,
            types.Part.from_bytes(
                data=place_bytes,
                mime_type= place_image.content_type,
            )
        ]

        contents.extend(furniture_parts)

        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
            )
        )


        print(response)
        
        image_data = None
        text_response = "No Description available."
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
        generated_image_storage_url = None
        original_image_storage_url = None

        if image_data:
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            image_url = f"data:{image_mime_type};base64,{image_base64}"

            # Store original image to Supabase storage
            try:
                original_ext = place_image.filename.split(".")[-1] if place_image.filename else "jpg"
                original_filename = f"original_{uuid.uuid4()}.{original_ext}"
                original_path = f"room-designs/originals/{original_filename}"

                supabase.storage.from_("room-images").upload(
                    path=original_path,
                    file=place_bytes,
                    file_options={"content-type": place_image.content_type}
                )
                original_image_storage_url = supabase.storage.from_("room-images").get_public_url(original_path)
            except Exception as storage_err:
                print(f"Failed to store original image: {storage_err}")

            # Store generated image to Supabase storage
            try:
                generated_filename = f"generated_{uuid.uuid4()}.png"
                generated_path = f"room-designs/generated/{generated_filename}"

                supabase.storage.from_("room-images").upload(
                    path=generated_path,
                    file=image_data,
                    file_options={"content-type": image_mime_type}
                )
                generated_image_storage_url = supabase.storage.from_("room-images").get_public_url(generated_path)
            except Exception as storage_err:
                print(f"Failed to store generated image: {storage_err}")
        else:
            image_url = None

        # Save to database if we have both URLs
        design_id = None
        if original_image_storage_url and generated_image_storage_url:
            try:
                db_response = supabase.table("room_designs").insert({
                    "original_image_url": original_image_storage_url,
                    "generated_image_url": generated_image_storage_url,
                    "design_type": design_type,
                    "room_type": room_type,
                    "style": style,
                    "background_color": background_color,
                    "foreground_color": foreground_color,
                    "instructions": instructions,
                    "description": text_response
                }).execute()

                if db_response.data:
                    design_id = db_response.data[0]["id"]
            except Exception as db_err:
                print(f"Failed to save to database: {db_err}")

        return JSONResponse(
        content={
            "image": image_url,
            "text": text_response,
            "design_id": design_id,
            "generated_image_url": generated_image_storage_url
        }
        )

    except Exception as e:
        print(f"Error in /api/try-on endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
