import { app } from "../../../scripts/app.js";

const MAX_INPUTS = 20;

function findLastConnected(node) {
    let last = 0;
    for (const inp of node.inputs) {
        if (inp.name?.startsWith("input_") && inp.link) {
            const num = parseInt(inp.name.split("_")[1]);
            if (num > last) last = num;
        }
    }
    return last;
}

function rebuildInputs(node) {
    // Find last connected input
    const lastConnected = findLastConnected(node);

    // Target: input_1 .. input_{lastConnected+1}, max MAX_INPUTS
    const targetCount = Math.min(lastConnected + 1, MAX_INPUTS);

    // Remove excess inputs from the end
    for (let i = node.inputs.length - 1; i >= 0; i--) {
        const inp = node.inputs[i];
        if (inp.name?.startsWith("input_")) {
            const num = parseInt(inp.name.split("_")[1]);
            if (num > targetCount) {
                node.removeInput(i);
            }
        }
    }

    // Add missing inputs
    for (let n = 1; n <= targetCount; n++) {
        const name = `input_${n}`;
        if (!node.inputs.find(i => i.name === name)) {
            node.addInput(name, "*");
        }
    }

    // Update select widget max and clamp value
    const selectWidget = node.widgets?.find(w => w.name === "select");
    if (selectWidget) {
        const maxVal = node.inputs.length;
        selectWidget.options.max = maxVal;
        if (selectWidget.value > maxVal) {
            selectWidget.value = maxVal;
        }
        updateOutputLabel(node);
    }
}

function updateOutputLabel(node) {
    const selectWidget = node.widgets?.find(w => w.name === "select");
    if (selectWidget && node.outputs?.[0]) {
        node.outputs[0].label = `\u2192 \u0432\u0445\u043e\u0434 ${selectWidget.value}`;
        node.graph?.setDirtyCanvas(true, true);
    }
}

app.registerExtension({
    name: "Degg.Switch",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "DeggSwitch") return;

        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const ret = origOnNodeCreated?.apply(this, arguments);

            const selectWidget = this.widgets?.find(w => w.name === "select");

            // Update output label when select changes
            if (selectWidget) {
                selectWidget.options.max = MAX_INPUTS;
                const origCb = selectWidget.callback;
                selectWidget.callback = function (value) {
                    if (origCb) origCb(value);
                    updateOutputLabel(this);
                };
            }

            // Rebuild to initial state (only input_1)
            rebuildInputs(this);

            return ret;
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
            const ret = onConnectionsChange?.apply(this, arguments);

            // type === 1 means input connection changed
            if (type === 1) {
                // Use setTimeout to avoid modifying inputs during connection processing
                setTimeout(() => {
                    rebuildInputs(this);
                }, 0);
            }

            return ret;
        };
    },
});
