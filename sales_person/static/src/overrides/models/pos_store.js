/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, "pos_sales_person/PosStore", {

    async _processData(loadedData) {
        await super._processData(...arguments);

        // Load employees into POS
        this.employees = loadedData["hr.employee"] || [];

        // Build employeeById map
        this.employeeById = {};
        for (const emp of this.employees) {
            this.employeeById[emp.id] = emp;
        }

        // Filter allowed sales persons from POS config
        if (this.config.sales_person_ids?.length) {
            this.allowedSalesPersons = this.config.sales_person_ids
                .map(id => this.employeeById[id])
                .filter(emp => !!emp);
        } else {
            this.allowedSalesPersons = this.employees;
        }
    },

});
