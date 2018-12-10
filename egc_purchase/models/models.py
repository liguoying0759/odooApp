# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class EgcPurchase(models.Model):
    _inherit = 'sale.order'

    num = fields.Integer(string='次数')


class EgcMo(models.Model):
    _inherit = 'mrp.production'

    num = fields.Integer(string='次数')


class EgcPurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    sku = fields.Char(string='客人SKU号')


class EgcPurchase(models.Model):
    _inherit = 'purchase.order'

    description = fields.Char(string='备注')

    # 获取默认的销售渠道
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    team_id1 = fields.Many2one('crm.team', '采购渠道', change_default=True, default=_get_default_team,
                               oldname='section_id')

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    dest_address_id = fields.Many2one('res.partner', string='送货地址', states=READONLY_STATES, \
                                      help="Put an address if you want to deliver directly from the vendor to the customer. " \
                                           "Otherwise, keep empty to deliver to your own company.")

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'Boss审核'),
        ('manage_approve', '经理审核'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    # so跟po单号对应
    @api.model
    def create(self, vals):
        # a = ''
        # res = ''
        if vals.get('origin'):
            origin = vals.get('origin')
            if origin[0:4] == 'DRSO':
                a = self.env['sale.order'].search([('name', '=', origin)])
                a.num += 1
                res = a.name[4:]
                value = 'DRPO' + res
                value = value + '-' + str(a.num)
                vals['name'] = value
                return super(EgcPurchase, self).create(vals)
            elif origin[0:4] == 'SMSO':
                a = self.env['sale.order'].search([('name', '=', origin)])
                a.num += 1
                res = a.name[4:]
                value = 'SMPO' + res
                value = value + '-' + str(a.num)
                vals['name'] = value
                return super(EgcPurchase, self).create(vals)
            # elif origin[0:2] == 'MO':
            #     a = self.env['mrp.production'].search([('name', '=', origin)])
            #     a.num += 1
            #     res = a.name[4:]
            #     value = 'DRPO' + res
            #     value = value + '-' + str(a.num)
            #     vals['name'] = value
            #     return super(EgcPurchase, self).create(vals)
        if vals.get('name', 'New') == 'New':
            value = self.env['ir.sequence'].next_by_code('purchase.order')
            if value:
                vals['name'] = value
            else:
                vals['name'] = '/'
        return super(EgcPurchase, self).create(vals)

    # 审批流程，老板开单或者金额不够或者不需要审批则直接开单
    @api.multi
    def button_approve_manage(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'manage_approve']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id.compute(
                        order.company_id.po_double_validation_amount, order.currency_id)) \
                    or order.user_has_groups('base.group_erp_manager'):
                order.button_approve()
                # print(self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))
            else:
                order.write({'state': 'to approve'})
        return True

    # 进入经理审核步骤
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            if order.user_has_groups('base.group_erp_manager'):
                order.button_approve_manage()
            elif order.user_has_groups('purchase.group_purchase_manager'):
                # order.write({'state': 'to approve'})
                order.button_approve_manage()
            else:
                order.write({'state': 'manage_approve'})
        return True


class EGCStockMove(models.Model):
    _inherit = 'stock.move'

    info_time = fields.Datetime(string='警告时间',compute='_compute_time')

    def _compute_time(self):
        for i in self:
            i.info_time = fields.datetime.now() + datetime.timedelta(days=7)
            # i.info_time = fields.Datetime.to_string(fields.datetime.now() + datetime.timedelta(days=7))
