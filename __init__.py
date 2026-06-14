import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from .excel_styles_loader import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

JS_DIR = os.path.join(current_dir, "js")
os.makedirs(JS_DIR, exist_ok=True)

JAVASCRIPT_CODE = """
import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "ExcelStylesLoader.DynamicDropdown",
    async beforeRegisterNodeDef(nodeType, nodeData, appInstance) {
        if (nodeData.name === "ExcelStylesLoader") {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                
                const tabWidget = this.widgets.find(w => w.name === "tab_name");
                const styleWidget = this.widgets.find(w => w.name === "style_name");
                
                // Force the widget property configuration to render explicitly as a combo dropdown menu
                if (styleWidget) {
                    styleWidget.type = "combo";
                }

                const updateStyles = async (tabValue) => {
                    if (!tabValue || !styleWidget) return;
                    try {
                        const response = await fetch(`/custom_nodes/excel_styles_loader/get_styles?tab_name=${encodeURIComponent(tabValue)}`);
                        const data = await response.json();
                        
                        if (data && data.styles) {
                            styleWidget.options.values = data.styles;
                            
                            if (!data.styles.includes(styleWidget.value)) {
                                styleWidget.value = data.styles.length > 0 ? data.styles[0] : "";
                            }
                            app.canvas.setDirty(true, true);
                        }
                    } catch (error) {
                        console.error("Error updating dynamic excel style widgets:", error);
                    }
                };

                if (tabWidget) {
                    tabWidget.callback = async (value) => {
                        await updateStyles(value);
                    };
                    
                    // Delay slightly to ensure layout initialization is ready before first read
                    setTimeout(() => {
                        updateStyles(tabWidget.value);
                    }, 50);
                }
            };
        }
    }
});
"""

try:
    js_file_path = os.path.join(JS_DIR, "excel_styles_loader.js")
    with open(js_file_path, "w", encoding="utf-8") as f:
        f.write(JAVASCRIPT_CODE.strip())
except Exception as e:
    print(f"[ExcelStylesLoader] Failed to write UI web script asset: {e}")

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]