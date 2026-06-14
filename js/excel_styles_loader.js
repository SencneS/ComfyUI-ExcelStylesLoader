import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "ExcelStylesLoader.DynamicDropdown",
    
    async beforeRegisterNodeDef(nodeType, nodeData, appInstance) {
        if (nodeData.name !== "ExcelStylesLoader") return;
        
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        
        nodeType.prototype.onNodeCreated = function () {
            origOnNodeCreated?.apply(this, arguments);
            
            const tabWidget = this.widgets.find(w => w.name === "tab_name");
            const styleWidget = this.widgets.find(w => w.name === "style_name");
            if (!tabWidget || !styleWidget) return;
            
            // ── State ──────────────────────────────────────────────────────
            const _tabCache = new Map();      // tabName -> [styleNames]
            let _currentTab = null;
            let _isRefreshing = false;        // lock to prevent concurrent fetches
            
            // ── Helpers ────────────────────────────────────────────────────
            
            const applyStyleOptions = (styles, preserveValue = false) => {
                styleWidget.options.values = styles;
                
                if (!preserveValue || !styles.includes(styleWidget.value)) {
                    styleWidget.value = styles.length > 0 ? styles[0] : "";
                }
                app.canvas.setDirty(true, true);
            };
            
            const fetchJson = async (url) => {
                const res = await fetch(url);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            };
            
            // ── Core: Load styles for a tab ──────────────────────────────
            
            const loadStyles = async (tabName, {preserveValue = false, force = false} = {}) => {
                if (!tabName || tabName === "No Tabs Found") {
                    applyStyleOptions([]);
                    return;
                }
                
                const cacheKey = `${tabName}|${force ? Date.now() : 'cached'}`;
                const useCache = !force && _tabCache.has(tabName);
                
                if (useCache) {
                    applyStyleOptions(_tabCache.get(tabName), preserveValue);
                    return;
                }
                
                try {
                    const forceParam = force ? "&force=1" : "";
                    const data = await fetchJson(
                        `/custom_nodes/excel_styles_loader/get_styles?tab_name=${encodeURIComponent(tabName)}${forceParam}`
                    );
                    
                    const styles = data.styles || [];
                    _tabCache.set(tabName, styles);
                    applyStyleOptions(styles, preserveValue);
                    
                } catch (err) {
                    console.error("[ExcelStylesLoader] Failed to load styles:", err);
                    applyStyleOptions([]);
                }
            };
            
            // ── Core: Full refresh (tabs + styles) ────────────────────────
            
            const fullRefresh = async ({fromUser = false} = {}) => {
                if (_isRefreshing) return;
                _isRefreshing = true;
                
                try {
                    const forceParam = fromUser ? "?force=1" : "";
                    const data = await fetchJson(`/custom_nodes/excel_styles_loader/get_tabs${forceParam}`);
                    const tabs = data.tabs || [];
                    
                    const oldTab = tabWidget.value;
                    const oldTabs = [...tabWidget.options.values];
                    
                    // Update tab widget
                    tabWidget.options.values = tabs.length > 0 ? tabs : ["No Tabs Found"];
                    
                    // Restore or pick best tab
                    if (tabs.includes(oldTab)) {
                        tabWidget.value = oldTab;
                    } else {
                        tabWidget.value = tabs.length > 0 ? tabs[0] : "No Tabs Found";
                    }
                    
                    // Clear style cache if tabs changed
                    const tabsChanged = oldTabs.length !== tabs.length ||
                        oldTabs.some((t, i) => t !== tabs[i]);
                    
                    if (tabsChanged || fromUser) {
                        _tabCache.clear();
                    }
                    
                    // Load styles for current tab
                    _currentTab = tabWidget.value;
                    await loadStyles(_currentTab, {
                        preserveValue: !tabsChanged, 
                        force: fromUser
                    });
                    
                    app.canvas.setDirty(true, true);
                    
                } catch (err) {
                    console.error("[ExcelStylesLoader] Refresh failed:", err);
                } finally {
                    _isRefreshing = false;
                }
            };
            
            // ── Hook: Tab dropdown opened ────────────────────────────────
            // Detect when user clicks the tab dropdown
            
            const origTabMouseDown = tabWidget.mouse ? tabWidget.mouse.bind(tabWidget) : null;
            
            // LiteGraph combo widgets expose onMenuShown or we can hook the element
            // More reliable: override the widget's onDraw to detect interaction,
            // but simplest is to hook the canvas mousedown near the widget
            
            const hookWidgetOpen = (widget, callback) => {
                // Store original mousedown handler if any
                const origMouseDown = widget.onMouseDown;
                
                widget.onMouseDown = function(e, localPos, node) {
                    // e is canvas event; check if clicking the dropdown arrow area
                    const result = origMouseDown?.apply(this, arguments);
                    
                    // LiteGraph: clicking anywhere on combo opens it
                    // We trigger refresh when user interacts with widget
                    callback();
                    return result;
                };
            };
            
            // Hook tab widget: refresh tabs when opened
            hookWidgetOpen(tabWidget, () => {
                fullRefresh({fromUser: true});
            });
            
            // Hook style widget: refresh styles when opened
            hookWidgetOpen(styleWidget, () => {
                loadStyles(tabWidget.value, {preserveValue: true, force: true});
            });
            
            // ── Hook: Tab selection change ───────────────────────────────
            
            const origTabCallback = tabWidget.callback;
            tabWidget.callback = async (value) => {
                origTabCallback?.call(tabWidget, value);
                _currentTab = value;
                await loadStyles(value, {preserveValue: false, force: true});
            };
            
            // ── Hook: Double-click anywhere on node ──────────────────────
            
            const origDblClick = this.onDblClick;
            this.onDblClick = function(e) {
                console.log("[ExcelStylesLoader] Manual refresh triggered");
                fullRefresh({fromUser: true});
                return origDblClick?.apply(this, arguments);
            };
            
            // ── Hook: Right-click context menu ───────────────────────────
            
            const origGetMenuOptions = this.getExtraMenuOptions;
            this.getExtraMenuOptions = function(_, options) {
                options.unshift({
                    content: "🔄 Refresh Excel Styles",
                    callback: () => fullRefresh({fromUser: true})
                });
                return origGetMenuOptions?.apply(this, arguments) || options;
            };
            
            // ── Initialization ─────────────────────────────────────────
            
            const init = async () => {
                _currentTab = tabWidget.value;
                // Initial load without force (use cache if valid)
                await fullRefresh({fromUser: false});
            };
            
            if (appInstance.graph) {
                init();
            } else {
                setTimeout(init, 100);
            }
        };
    }
});