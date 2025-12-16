/** @odoo-module **/
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
 setup(vals) {
        super.setup(vals);

        },


export_for_printing(...args) {
    const result = super.export_for_printing(...args);
    result.selected_employee_name = this.selected_employee_id
        ? this.selected_employee_id.name
        : "";
    return result;
}
});
