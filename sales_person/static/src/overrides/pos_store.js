/** @odoo-module alias="@point_of_sale/app/services/pos_store" **/

import { PosStore } from "@point_of_sale/app/services/pos_store";

PosStore.prototype._processData = (function (superFn) {
    return function (data) {
        superFn.call(this, data);

        const Order = this.models.Order;

        Order.prototype.setup = function () {
            Order.prototype.__proto__.setup.call(this);
            this.sales_person = this.sales_person || false;
        };

        Order.prototype.set_sales_person = function (employee) {
            this.sales_person = employee;
            this.trigger("change");
        };

        Order.prototype.get_sales_person = function () {
            return this.sales_person;
        };

        Order.prototype.export_as_JSON = function () {
            const json = Order.prototype.__proto__.export_as_JSON.call(this);
            json.sales_person_id = this.sales_person ? this.sales_person.id : false;
            return json;
        };

        Order.prototype.init_from_JSON = function (json) {
            Order.prototype.__proto__.init_from_JSON.call(this, json);
            if (json.sales_person_id) {
                this.sales_person = this.pos.employees.find(
                    (e) => e.id === json.sales_person_id
                );
            }
        };
    };
})(PosStore.prototype._processData);
