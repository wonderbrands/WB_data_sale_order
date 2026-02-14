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

    # Comentar si modulo wms_integrator se queda
    data_total_carrier_tracking = fields.Integer(string="Total de guias")
    
    
    data_availability = fields.Boolean(string='Disponibilidad', help='Venta negada o cancelada por disponibilidad')
    data_delivery_time = fields.Boolean(string='Tiempo de entrega', help='Venta negada o cancelada por tiempo de entrega')
    data_sale_price = fields.Boolean(string='Precio de venta', help='Venta negada o cancelada por precio de venta')
    data_other = fields.Boolean(string='Otra', help='Venta negada o cancelada por una razón que no se encuentra en el listado')
    data_message = fields.Text(string='¿Cuál es el motivo?', help='Anote la razón por la cual se negó o canceló la venta', tracking=True) # track_visibility=True  No funiona ya
    data_time_zone = fields.Datetime(string='Zona horaria', help='Prueba de la zona horaria')

    data_auto_invoiced = fields.Boolean(string='Fue autofacturado',help='Muestra si la SO activa fue facturada de manera automática')
    
    

    @api.onchange('data_other')
    def _clear_field(self):

        if not self.data_other:
            self.data_message = False
            
            
# Comentar si modulo wms_integrator se queda

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

    carrier_selection_relational = fields.Many2one(
        name = "Select carrier",
        comodel_name = "carriers.list",
    )

