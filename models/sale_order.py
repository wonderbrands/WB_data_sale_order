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
    # data_total_carrier_tracking = fields.Integer(string="Total de guias")
    
    data_availability = fields.Boolean(string='Disponibilidad', help='Venta negada o cancelada por disponibilidad')
    data_delivery_time = fields.Boolean(string='Tiempo de entrega', help='Venta negada o cancelada por tiempo de entrega')
    data_sale_price = fields.Boolean(string='Precio de venta', help='Venta negada o cancelada por precio de venta')
    data_other = fields.Boolean(string='Otra', help='Venta negada o cancelada por una razón que no se encuentra en el listado')
    data_message = fields.Text(string='¿Cuál es el motivo?', help='Anote la razón por la cual se negó o canceló la venta', tracking=True)
    data_time_zone = fields.Datetime(string='Zona horaria', help='Prueba de la zona horaria')

    # Comentado el 25 feb 2026, no se usa
    # data_auto_invoiced = fields.Boolean(string='Fue autofacturado',help='Muestra si la SO activa fue facturada de manera automática')
    
    # --- CAMPO CORREGIDO DE CARRIER ---
    data_carrier_selection_relational = fields.Many2one(
        comodel_name="carriers.list",
        string="Select carrier" # Corregido: antes decía name="Select carrier", lo cual causaba errores en vistas
    )

    # --- NUEVO CAMPO: READY TO PICK ---
    data_ready_to_pick = fields.Boolean(
        string='Listo para recolectar',
        compute='_compute_data_ready_to_pick',
        store=True,
        help='Indica si el pedido tiene número de guía y al menos un documento adjunto.'
    )
        
    data_attachment_ids = fields.One2many(
        comodel_name='sale.order.attachment',
        inverse_name='so_id',
        string='Adjuntos de la orden'
    )
    

    @api.onchange('data_other')
    def _clear_field(self):
        # Siempre iterar sobre self en métodos de Odoo para evitar errores de singleton
        for record in self:
            if not record.data_other:
                record.data_message = False

    @api.depends('yuju_carrier_tracking_ref', 'data_attachment_ids')
    def _compute_data_ready_to_pick(self):
        for order in self:
            has_tracking = bool(order.yuju_carrier_tracking_ref)
            attachment_count = len(order.data_attachment_ids)
            
            order.data_ready_to_pick = has_tracking and (attachment_count > 0)


# Comentar si modulo wms_integrator se queda
class CarrierSelector(models.Model):
    _name = "carriers.list"
    _description = "Carrier List"

    name = fields.Char(
        string="Carrier Name",
        required=True,
        index=True
    )

    code = fields.Char(
        string="Carrier internal code",
        required=True
    )

    full_name = fields.Char(
        string="Full Name",
        compute='_compute_name',
        store=False
    )

    @api.depends('name', 'code')
    def _compute_name(self):
        for record in self:
            # Manejo seguro por si code o name llegan como False
            code_str = record.code or ''
            name_str = record.name or ''
            record.full_name = f"{code_str} - {name_str}"