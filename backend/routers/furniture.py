from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from config.supabase_client import supabase
import uuid
import traceback

router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
MAX_IMAGE_SIZE_MB = 10

@router.post("/furniture/upload")
async def upload_furniture(
    furniture_image: UploadFile = File(...),
    name: str = Form(...),
    category: str = Form(...),
):
    try:
        if furniture_image.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {furniture_image.content_type}")

        furniture_bytes = await furniture_image.read()
        if len(furniture_bytes) / (1024*1024) > MAX_IMAGE_SIZE_MB:
            raise HTTPException(status_code=400, detail="Image exceeds 10MB size limit")

        ext = furniture_image.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{ext}"
        storage_path = f"furniture/{unique_filename}"

        upload_response = supabase.storage.from_("furniture-images").upload(
            path=storage_path,
            file=furniture_bytes,
            file_options={"content-type": furniture_image.content_type}
        )
        if hasattr(upload_response, "error") and upload_response.error:
            raise HTTPException(status_code=500, detail=f"Storage upload failed: {upload_response.error}")

        public_url = supabase.storage.from_("furniture-images").get_public_url(storage_path)

        db_response = supabase.table("furniture_items").insert({
            "name": name,
            "category": category,
            "image_url": public_url,
            "user_id": None
        }).execute()

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Failed to save furniture to database")

        return JSONResponse({
            "id": db_response.data[0]["id"],
            "name": name,
            "category": category,
            "image_url": public_url,
            "message": "Furniture uploaded successfully"
        })

    except Exception as e:
        print(f"Upload error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/furniture/list")
async def list_furniture(category: str = None):
    try:
        query = supabase.table("furniture_items").select("*").order("created_at", desc=True)
        if category:
            query = query.eq("category", category)
        response = query.execute()
        return JSONResponse({"furniture": response.data or []})
    except Exception as e:
        print(f"List error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/furniture/{furniture_id}")
async def delete_furniture(furniture_id: str):
    try:
        res = supabase.table("furniture_items").select("image_url").eq("id", furniture_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Furniture not found")

        storage_path = res.data[0]["image_url"].split("/furniture-images/")[-1]
        supabase.storage.from_("furniture-images").remove([storage_path])
        supabase.table("furniture_items").delete().eq("id", furniture_id).execute()

        return JSONResponse({"message": "Furniture deleted successfully"})
    except Exception as e:
        print(f"Delete error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
