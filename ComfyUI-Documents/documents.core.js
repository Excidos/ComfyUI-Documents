import { app } from '../../../scripts/app.js';
import { api } from '../../../scripts/api.js';

function chainCallback(object, property, callback) {
    if (object == undefined) {
        console.error("Tried to add callback to non-existent object");
        return;
    }
    if (property in object) {
        const callback_orig = object[property];
        object[property] = function () {
            const r = callback_orig.apply(this, arguments);
            callback.apply(this, arguments);
            return r;
        };
    } else {
        object[property] = callback;
    }
}

function searchBox(event, [x, y], node) {
    if (this.prompt) {
        return;
    }
    this.prompt = true;

    let pathWidget = this;
    let dialog = document.createElement("div");
    dialog.className = "litegraph litesearchbox graphdialog rounded";
    dialog.innerHTML = '<span class="name">File Path</span> <input autofocus="" type="text" class="value"><button class="rounded">OK</button><div class="helper"></div>';
    dialog.close = () => {
        dialog.remove();
    };
    document.body.append(dialog);
    if (app.canvas.ds.scale > 1) {
        dialog.style.transform = "scale(" + app.canvas.ds.scale + ")";
    }
    var input = dialog.querySelector(".value");
    var options_element = dialog.querySelector(".helper");
    input.value = pathWidget.value || "";

    var timeout = null;
    let last_path = null;
    let extensions = pathWidget.options?.extensions;

    input.addEventListener("keydown", (e) => {
        dialog.is_modified = true;
        if (e.keyCode == 27) {
            dialog.close();
        } else if (e.keyCode == 13 && e.target.localName != "textarea") {
            if (pathWidget.value) {
                pathWidget.value = input.value;
                if (pathWidget.callback) {
                    pathWidget.callback(pathWidget.value);
                }
            }
            dialog.close();
        } else {
            if (timeout) {
                clearTimeout(timeout);
            }
            timeout = setTimeout(updateOptions, 100);
            return;
        }
        this.prompt = false;
        e.preventDefault();
        e.stopPropagation();
    });

    var button = dialog.querySelector("button");
    button.addEventListener("click", (e) => {
        if (pathWidget.value) {
            pathWidget.value = input.value;
            if (pathWidget.callback) {
                pathWidget.callback(pathWidget.value);
            }
        }
        node.graph.setDirtyCanvas(true);
        dialog.close();
        this.prompt = false;
    });

    var rect = app.canvas.canvas.getBoundingClientRect();
    var offsetx = -20;
    var offsety = -20;
    if (rect) {
        offsetx -= rect.left;
        offsety -= rect.top;
    }

    if (event) {
        dialog.style.left = event.clientX + offsetx + "px";
        dialog.style.top = event.clientY + offsety + "px";
    } else {
        dialog.style.left = canvas.width * 0.5 + offsetx + "px";
        dialog.style.top = canvas.height * 0.5 + offsety + "px";
    }

    async function updateOptions() {
        timeout = null;
        let params = { path: input.value };
        if (extensions) {
            params.extensions = extensions;
        }
        let optionsURL = api.apiURL('getpath?' + new URLSearchParams(params));
        try {
            let resp = await fetch(optionsURL);
            let options = await resp.json();
            options_element.innerHTML = '';
            for (let option of options) {
                let el = document.createElement("div");
                el.innerText = option;
                el.className = "litegraph lite-search-item";
                if (option.endsWith('/')) {
                    el.className += " is-dir";
                    el.addEventListener("click", (e) => {
                        input.value = option;
                        if (timeout) {
                            clearTimeout(timeout);
                        }
                        timeout = setTimeout(updateOptions, 100);
                    });
                } else {
                    el.addEventListener("click", (e) => {
                        if (pathWidget.value) {
                            pathWidget.value = option;
                            if (pathWidget.callback) {
                                pathWidget.callback(pathWidget.value);
                            }
                        }
                        dialog.close();
                        pathWidget.prompt = false;
                    });
                }
                options_element.appendChild(el);
            }
        } catch (e) {
            console.error("Error fetching options:", e);
        }
    }

    setTimeout(async function () {
        input.focus();
        await updateOptions();
    }, 100);

    return dialog;
}

app.registerExtension({
    name: "ComfyUI-Documents",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData?.name == "DocumentLoader" || nodeData?.name == "PDFToImage") {
            chainCallback(nodeType.prototype, "onNodeCreated", function () {
                const pathWidget = this.widgets.find((w) => w.name === "document");
                pathWidget.mouse = searchBox;
            });
        }
    }
});