/** @odoo-module **/

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, "pos_sales_person/Order", {

    setup() {
        super.setup(...arguments);
        this.sales_person = this.sales_person || false;
    },

    clone() {
        const order = super.clone(...arguments);
        order.sales_person = this.get_sales_person() || false;
        return order;
    },

    export_for_printing() {
        const order = super.export_for_printing(...arguments);
        order.sales_person = this.is_sales_person_set()
            ? this.get_sales_person().name
            : false;
        return order;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.sales_person_id = this.is_sales_person_set()
            ? this.get_sales_person().id
            : false;
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        let sales_person = false;

        if (json.sales_person_id) {
            sales_person = this.get_sales_person_by_id(json.sales_person_id);
            if (!sales_person) {
                console.error(
                    "ERROR: trying to load an employee not available in the POS"
                );
            }
        }

        this.set_sales_person(sales_person);
    },

    get_sales_person_by_id(id) {
        return this.pos.employeeById[id] || false;
    },

    is_sales_person_set() {
        return !!this.get_sales_person();
    },

    get_sales_person() {
        return this.sales_person;
    },

    set_sales_person(sales_person) {
        this.sales_person = sales_person;
        this.trigger("change", this);
    },

    removeOrderline(line) {
        super.removeOrderline(...arguments);
        if (this.orderlines.length <= 0) {
            this.set_sales_person(false);
        }
    },
});
