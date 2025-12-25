odoo.define('oxord_repair.sale_order_confirm', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var core = require('web.core');

    FormController.include({
        _onButtonClicked: function (event) {
            var self = this;

            if (event.data.attrs.name === 'action_confirm') {
                // Show confirmation dialog
                this.do_warn(
                    _t("Confirm Quotation"),
                    _t("Are you sure you want to confirm this quotation?"),
                    {
                        confirm_callback: function () {
                            // Call original button action after confirmation
                            self._super(event);
                        }
                    }
                );
                return;
            }

            return this._super(event);
        },
    });
});
