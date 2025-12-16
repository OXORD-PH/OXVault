/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class SalespersonPopup extends Component {
    setup() {
        this.state = useState({
            search: "",
        });
    }

    get filteredEmployees() {
        const employees = this.props.employees || [];
        const search = this.state.search.toLowerCase();
        return employees.filter((emp) =>
            emp.name.toLowerCase().includes(search)
        );
    }

    selectEmployee(employee) {
        this.props.onSelect(employee);
        this.props.close();
    }
}

SalespersonPopup.template = "salesperson.SalespersonPopup";

registry.category("pos_popups").add("SalespersonPopup", SalespersonPopup);
