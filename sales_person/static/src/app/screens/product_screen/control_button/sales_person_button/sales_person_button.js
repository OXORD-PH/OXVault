/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class SalesPersonButton extends Component {
    static template = "pos_sales_person.SalesPersonButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        const order = this.pos.get_order();
        if (!order) return;
        if (order.orderlines.length <= 0) return;

        const employeesList = this.pos.employees
            .filter((employee) =>
                order.get_sales_person()
                    ? employee.id !== order.get_sales_person().id
                    : true
            )
            .map((employee) => {
                return {
                    id: employee.id,
                    item: employee,
                    label: employee.name,
                    isSelected: false,
                };
            });

        if (!employeesList.length) return;

        const { confirmed, payload: employee } = await this.popup.add(
            SelectionPopup,
            {
                title: _t("Select Sales Person"),
                list: employeesList,
            }
        );

        if (!confirmed || !employee) return;

        order.set_sales_person(employee);
    }
}

ProductScreen.addControlButton({
    component: SalesPersonButton,
});
