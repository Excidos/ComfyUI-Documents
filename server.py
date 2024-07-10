import server
import os
from aiohttp import web
from .utils import is_safe_path, strip_path
from .utils import folder_paths  # Import folder_paths from utils

routes = server.PromptServer.instance.routes

@routes.post("/upload/document")
async def upload_document(request):
    try:
        data = await request.post()
        file = data['document']
        filename = file.filename
        content = file.file.read()
        
        input_dir = folder_paths.get_input_directory()
        file_path = os.path.join(input_dir, filename)
        
        if not is_safe_path(file_path):
            return web.Response(status=403, text="Invalid file path")
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return web.json_response({"name": filename})
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        return web.Response(status=500, text=str(e))

@routes.get("/getpath")
async def get_path(request):
    query = request.rel_url.query
    if "path" not in query:
        return web.Response(status=400, text="Missing 'path' parameter")
    path = os.path.abspath(strip_path(query["path"]))

    if not os.path.exists(path) or not is_safe_path(path):
        return web.json_response([])

    valid_extensions = query.get("extensions", "").split(",")
    valid_items = []
    for item in os.scandir(path):
        try:
            if item.is_dir():
                valid_items.append(item.name + "/")
                continue
            if not valid_extensions or item.name.split(".")[-1].lower() in valid_extensions:
                valid_items.append(item.name)
        except OSError:
            pass

    return web.json_response(valid_items)

WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "web")