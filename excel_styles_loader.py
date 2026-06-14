import os
import openpyxl
from server import PromptServer
from aiohttp import web

_EXCEL_CACHE = {}

def get_filepath():
    """Returns the absolute path to styles.xlsx inside this node's folder."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.xlsx")

def load_excel_data():
    """Parses styles.xlsx mapping sheet names to their rows."""
    filepath = get_filepath()
    if not os.path.exists(filepath):
        return {"Error: styles.xlsx missing": {"Place file in node folder": ["", ""]}}

    data = {}
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            data[sheet_name] = {}
            
            rows = list(sheet.iter_rows(values_only=True))
            if not rows or len(rows) <= 1:
                continue
            
            headers = [str(c).strip().lower() if c is not None else "" for c in rows[0]]
            
            name_idx = headers.index("name") if "name" in headers else 0
            pos_idx = headers.index("prompt") if "prompt" in headers else 1
            neg_idx = headers.index("negative_prompt") if "negative_prompt" in headers else 2
            
            for row in rows[1:]:
                if not row or row[name_idx] is None:
                    continue
                
                style_name = str(row[name_idx]).strip()
                if not style_name:
                    continue
                    
                pos_val = str(row[pos_idx]).strip() if len(row) > pos_idx and row[pos_idx] is not None else ""
                neg_val = str(row[neg_idx]).strip() if len(row) > neg_idx and row[neg_idx] is not None else ""
                
                data[sheet_name][style_name] = [pos_val, neg_val]
        return data
    except Exception as e:
        print(f"[ExcelStylesLoader] Error reading workbook: {e}")
        return {f"Error: {str(e)}": {"Check file formatting": ["", ""]}}

@PromptServer.instance.routes.get("/custom_nodes/excel_styles_loader/get_styles")
async def get_styles_endpoint(request):
    tab_name = request.rel_url.query.get("tab_name", "")
    
    global _EXCEL_CACHE
    _EXCEL_CACHE = load_excel_data()
    
    styles_list = list(_EXCEL_CACHE[tab_name].keys()) if tab_name in _EXCEL_CACHE else []
    return web.json_response({"styles": styles_list})


class ExcelStylesLoader:
    @classmethod
    def INPUT_TYPES(cls):
        global _EXCEL_CACHE
        _EXCEL_CACHE = load_excel_data()
        
        tab_choices = list(_EXCEL_CACHE.keys())
        if not tab_choices:
            tab_choices = ["No Tabs Found"]
            
        # Give it a tiny default array to initialize as a genuine dropdown element
        return {
            "required": {
                "tab_name": (tab_choices,),
                "style_name": (["Select a Tab First"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive prompt", "negative prompt")
    FUNCTION = "execute"
    CATEGORY = "loaders"

    def execute(self, tab_name, style_name):
        global _EXCEL_CACHE
        if not _EXCEL_CACHE:
            _EXCEL_CACHE = load_excel_data()
            
        if tab_name in _EXCEL_CACHE and style_name in _EXCEL_CACHE[tab_name]:
            return (_EXCEL_CACHE[tab_name][style_name][0], _EXCEL_CACHE[tab_name][style_name][1])
            
        if tab_name in _EXCEL_CACHE and _EXCEL_CACHE[tab_name]:
            first_key = list(_EXCEL_CACHE[tab_name].keys())[0]
            return (_EXCEL_CACHE[tab_name][first_key][0], _EXCEL_CACHE[tab_name][first_key][1])
            
        return ("", "")

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """
        Bypasses strict backend verification list checking completely,
        preventing the 'Value not in list' crash during execution.
        """
        return True


NODE_CLASS_MAPPINGS = {
    "ExcelStylesLoader": ExcelStylesLoader
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ExcelStylesLoader": "Load Styles from Excel (.xlsx)"
}