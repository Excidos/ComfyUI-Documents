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

function createFileUploadWidget(node, inputName, inputData, app) {
    const fileInput = document.createElement("input");
    Object.assign(fileInput, {
        type: "file",
        accept: ".pdf,.txt,.doc,.docx",
        style: "display: none",
        onchange: async () => {
            if (fileInput.files.length) {
                await uploadFile(fileInput.files[0], true);
            }
        },
    });
    document.body.append(fileInput);

    const uploadWidget = node.addWidget("button", inputName, "document", () => {
        fileInput.click();
    });
    uploadWidget.label = "Choose file to upload";
    uploadWidget.serialize = false;

    async function uploadFile(file, updateNode) {
        try {
            const body = new FormData();
            body.append("document", file);
            const resp = await api.fetchApi("/upload/document", {
                method: "POST",
                body,
            });
            if (resp.status === 200) {
                const data = await resp.json();
                let path = data.name;
                if (data.subfolder) path = data.subfolder + "/" + path;
                
                let documentWidget = null;
                for (let i = 0; i < node.widgets.length; i++) {
                    if (node.widgets[i].name === "file_path") {
                        documentWidget = node.widgets[i];
                        break;
                    }
                }
                
                if (documentWidget && !documentWidget.options.values.includes(path)) {
                    documentWidget.options.values.push(path);
                }
                if (updateNode && documentWidget) {
                    documentWidget.value = path;
                }
            } else {
                alert(resp.status + " - " + resp.statusText);
            }
        } catch (error) {
            alert(error);
        }
    }

    node.onDragOver = function (e) {
        if (e.dataTransfer && e.dataTransfer.items) {
            const document = [...e.dataTransfer.items].find((f) => f.kind === "file" && 
                (f.type === "application/pdf" || f.type === "text/plain" || 
                 f.type === "application/msword" || f.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"));
            return !!document;
        }
        return false;
    };

    node.onDragDrop = function (e) {
        let handled = false;
        for (const file of e.dataTransfer.files) {
            if (file.type === "application/pdf" || file.type === "text/plain" || 
                file.type === "application/msword" || file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
                uploadFile(file, !handled);
                handled = true;
            }
        }
        return handled;
    };

    return { widget: uploadWidget };
}

app.registerExtension({
    name: "ComfyUI-Documents",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData?.name == "DocumentLoader" || nodeData?.name == "PDFToImage") {
            chainCallback(nodeType.prototype, "onNodeCreated", function () {
                let documentWidget = null;
                for (let i = 0; i < this.widgets.length; i++) {
                    if (this.widgets[i].name === "file_path") {
                        documentWidget = this.widgets[i];
                        break;
                    }
                }
                
                if (documentWidget) {
                    documentWidget.options.values = [];
                    api.fetchApi('/getpath?path=input&extensions=pdf,txt,doc,docx')
                        .then(response => response.json())
                        .then(files => {
                            documentWidget.options.values = files;
                            if (files.length > 0) {
                                documentWidget.value = files[0];
                            }
                        });
                }
                createFileUploadWidget(this, "upload_document", {}, app);
            });
        }
    }
});