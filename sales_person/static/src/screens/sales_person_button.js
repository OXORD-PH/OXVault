/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/components/popups/selection_popup/selection_popup";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { registry } from "@web/core/registry";

export class SalesPersonButton extends Component {
    static template = "sales_person.SalesPersonButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        const order = this.pos.get_order();
        if (!order || order.orderlines.length <= 0) return;

        const employeesList = (this.pos.employees || []).map((employee) => ({
            id: employee.id,
            item: employee,
            label: employee.name,
            isSelected:
                order.get_sales_person() &&
                employee.id === order.get_sales_person().id,
        }));

        const { confirmed, payload: employee } = await this.popup.add(
            SelectionPopup,
            {
                title: _t("Select Sales Person"),
                list: employeesList,
            }
        );

        if (confirmed && employee) {
            order.set_sales_person(employee);
        }
    }
}

// ------------------------------------------------------------
// REGISTER BUTTON IN ODOO 19 POS
// ------------------------------------------------------------
registry.category("pos_control_buttons").add("sales_person_button", {
    component: SalesPersonButton,
    condition: (env) => true,
    sequence: 15, // lower = earlier
});