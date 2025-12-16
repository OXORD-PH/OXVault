/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

const originalSetCashier = PosStore.prototype.set_cashier;

patch(PosStore.prototype, {
    set_cashier(employee) {
        originalSetCashier.call(this, employee);
        const order = this.get_order();
        if (order) {
            order.selected_employee_id = employee;
        }
    },
});
