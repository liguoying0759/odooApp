# -*- coding: utf-8 -*-
from odoo import http

# class EgcPurchase(http.Controller):
#     @http.route('/egc_purchase/egc_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/egc_purchase/egc_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('egc_purchase.listing', {
#             'root': '/egc_purchase/egc_purchase',
#             'objects': http.request.env['egc_purchase.egc_purchase'].search([]),
#         })

#     @http.route('/egc_purchase/egc_purchase/objects/<model("egc_purchase.egc_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('egc_purchase.object', {
#             'object': obj
#         })