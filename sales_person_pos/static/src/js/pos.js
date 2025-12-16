/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";

export class SelectEmployeeButton extends Component {
    static template = "sales_person_pos.SelectEmployeeButton";
    static props = {
        class: { type: String, optional: true },
    };

setup() {
    this.pos = usePos();
    this.dialog = useService("dialog");

    const order = this.pos.get_order();


    const current = order?.selected_employee_id;

    const config = this.pos.config;
    const allowedEmployeeIds = new Set(
        (config.basic_employee_ids || []).map((e) => e.id)
    );

    const employees = this.pos.models["hr.employee"]
        .getAll()
        .filter((emp) => allowedEmployeeIds.has(emp.id));

    this.state = useState({
        label: current ? current.name : _t("Employee"),
        avatar: current
            ? `/web/image?model=hr.employee&id=${current.id}&field=image_128`
            : "/web/static/img/user_placeholder.png",
    });

onMounted(async () => {
    const order = this.pos.get_order();
    const employee = order?.selected_employee_id;

    this.state.label = employee ? employee.name : _t("Employee");
    this.state.avatar =  await employee
        ? `/web/image?model=hr.employee&id=${employee.id}&field=image_128`
        : "/web/static/img/user_placeholder.png";
});
}
    async onClick() {
        const config = this.pos.config;
//        const allowedEmployeeIds = new Set(
//            (config.basic_employee_ids || []).map((e) => e.id)
//        );
        const employees = this.pos.models["hr.employee"].getAll()
//            .filter((emp) => allowedEmployeeIds.has(emp.id));

        if (!employees) {
            this.dialog.add(AlertDialog, {
                title: _t("No Employees"),
                body: _t("There are no employees allowed for this POS."),
            });
            return;
        }

        const selected = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select Employee"),
            list: employees.map((emp) => ({
                id: emp.id,
                label: emp.name,
                item: emp,
                avatar: `/web/image?model=hr.employee&id=${emp.id}&field=image_128`,
            })),
            getPayload: (selected) => selected.item,
        });

        if (selected) {
            const order = this.pos.get_order();
            order.selected_employee_id = selected;
            this.state.avatar = `/web/image?model=hr.employee&id=${selected.id}&field=image_128`;
             this.state.label = selected.name;
            this.pos.set_cashier(selected);
        }
    }
}

// Register the button in POS
patch(ControlButtons, {
    components: {
        ...ControlButtons.components,
        SelectEmployeeButton,
    },
});
