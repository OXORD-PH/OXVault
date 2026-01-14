/** @odoo-module **/

import { PosActionButton } from "@point_of_sale/app/screens/order_actions/pos_action_button";
import { registry } from "@web/core/registry";

class SalespersonActionButton extends PosActionButton {
    async onClick() {
        const users = this.env.pos.db.get_salespersons();
        if (!users || users.length === 0) {
            return;
        }

        const { confirmed, payload } = await this.showPopup("SelectionPopup", {
            title: "Select Salesperson",
            list: users.map(u => ({ id: u.id, label: u.name })),
        });

        if (confirmed) {
            this.currentOrder.setSalesperson(payload.id);
        }
    }

    isShown() {
        return true;  // always show
    }
}

// Register in the order actions menu
registry.category("pos_action_buttons").add("salesperson_action_button", SalespersonActionButton);
