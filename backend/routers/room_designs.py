from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from config.supabase_client import supabase
import traceback

router = APIRouter()

@router.get("/room-designs/list")
async def list_room_designs(limit: int = 50):
    try:
        response = supabase.table("room_designs").select("*").order("created_at", desc=True).limit(limit).execute()
        return JSONResponse({"designs": response.data or []})
    except Exception as e:
        print(f"List error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/room-designs/{design_id}")
async def get_room_design(design_id: str):
    try:
        response = supabase.table("room_designs").select("*").eq("id", design_id).maybeSingle().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Room design not found")
        return JSONResponse({"design": response.data})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/room-designs/{design_id}")
async def delete_room_design(design_id: str):
    try:
        res = supabase.table("room_designs").select("original_image_url, generated_image_url").eq("id", design_id).maybeSingle().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Room design not found")

        # Delete from storage
        try:
            if res.data["original_image_url"]:
                original_path = res.data["original_image_url"].split("/room-images/")[-1]
                supabase.storage.from_("room-images").remove([original_path])
        except Exception as storage_err:
            print(f"Failed to delete original image: {storage_err}")

        try:
            if res.data["generated_image_url"]:
                generated_path = res.data["generated_image_url"].split("/room-images/")[-1]
                supabase.storage.from_("room-images").remove([generated_path])
        except Exception as storage_err:
            print(f"Failed to delete generated image: {storage_err}")

        supabase.table("room_designs").delete().eq("id", design_id).execute()

        return JSONResponse({"message": "Room design deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
