from odoo import http
from odoo.http import request


class PosSalesPersonController(http.Controller):

    @http.route('/get_pos_sales_person', type='json', auth='user', methods=['POST'])
    def get_pos_sales_person(self, product_id, pos_order_line_id):
        product = request.env['product.product'].browse(product_id)
        sales_person_data = {
            'sales_person': product.pos_sales_person_id.name if product.pos_sales_person_id else ''
        }
        request.env['pos.order.line'].sudo().browse(int(pos_order_line_id)).write({
            'user_id': product.pos_sales_person_id.id
        })
        return sales_person_data
