/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { SalespersonPopup } from "./salesperson_popup";

patch(ProductScreen.prototype, {
    async onClickAddSalesperson() {
        const employees = this.env.services.pos.models["hr.employee"] || [];

        const { confirmed, payload } = await this.showPopup("SalespersonPopup", {
            employees: employees,
            onSelect: (employee) => {
                const order = this.currentOrder;
                order.salesperson = employee;
            },
        });

        if (confirmed && payload) {
            const order = this.currentOrder;
            order.salesperson = payload;
        }
    },
});
