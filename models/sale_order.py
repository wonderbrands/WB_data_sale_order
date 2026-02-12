# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from datetime import datetime
from pytz import timezone
import logging
import json
import requests

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    data_total_carrier_tracking = fields.Integer(
        string="Total de guias"
    )
    availability = fields.Boolean(string='Disponibilidad', help='Venta negada o cancelada por disponibilidad')
    delivery_time = fields.Boolean(string='Tiempo de entrega', help='Venta negada o cancelada por tiempo de entrega')
    sale_price = fields.Boolean(string='Precio de venta', help='Venta negada o cancelada por precio de venta')
    other = fields.Boolean(string='Otra', help='Venta negada o cancelada por una razón que no se encuentra en el listado')
    message = fields.Text(string='¿Cuál es el motivo?', help='Anote la razón por la cual se negó o canceló la venta', tracking=True) # track_visibility=True  No funiona ya
    time_zone = fields.Datetime(string='Zona horaria', help='Prueba de la zona horaria')

    auto_invoiced = fields.Boolean(string='Fue autofacturado',help='Muestra si la SO activa fue facturada de manera automática')
    
    

    @api.onchange('other')
    def _clear_field(self):

        if not self.other:
            self.message = False
            
            
# Se aniade modelo de carriers desde modulo WMS (deprecado para Odoo 18.0)
class CarrierSelector(models.Model):
    _name = "carriers.list"

    name = fields.Char(
        string = "Carrier Name",
        required = True,
        index = True
    )

    code = fields.Char(
        string = "Carrier internal code",
        required = True
    )

    full_name = fields.Char(compute='_compute_name')

    @api.depends('name', 'code')
    def _compute_name(self):
        for record in self:
            record.full_name = f"{'' if not record.code else record.code} - {'' if not record.name else record.name}"





class CarriersFields(models.Model):
    _inherit = 'sale.order'
    _description = 'Carrier fields'

    data_carrier_selection_relational = fields.Many2one(
        name = "Select carrier",
        comodel_name = "carriers.list",
        options={
            'no_create': True
        }
    )

