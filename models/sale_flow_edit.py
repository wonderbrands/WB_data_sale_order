# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SOAttachment(models.Model):
    _name = "sale.order.attachment"
    _description = "Anexos de Orden de Venta"
    _order = "sequence_number asc" 

    attachment = fields.Binary(string="Archivo", required=True)
    file_name = fields.Char(string="Nombre del Archivo")
    so_id = fields.Many2one("sale.order", string="Orden de Venta", ondelete='cascade')
    sequence_number = fields.Integer(string="Secuencia", readonly=True)
    display_name_custom = fields.Char(string="Referencia de Guía", compute="_compute_display_name_custom", store=True)
    

    on_bin = fields.Boolean(string="En bin", default=False)
    bin_id = fields.Many2one("bin.storage", string="BIN Actual", tracking=True)
    on_dock = fields.Boolean(string="Está en DOCK", default=False, tracking=True)
    dock_id = fields.Many2one("dock.storage", string="DOCK Actual", tracking=True)
    dispatched = fields.Boolean(string="Entregado a paquetería", default=False)

    @api.depends('so_id', 'sequence_number')
    def _compute_display_name_custom(self):
        for record in self:
            if record.so_id and record.sequence_number:
                record.display_name_custom = f"{record.so_id.name}/{record.sequence_number}"
            else:
                record.display_name_custom = "Nueva Guía"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('so_id'):
                #Calcula la secuencia sumando 1 al total de guías existentes
                existing_count = self.search_count([('so_id', '=', vals['so_id'])])
                vals['sequence_number'] = existing_count + 1
        return super(SOAttachment, self).create(vals_list)

    def unlink(self):
        #Guardamos los IDs de las SO afectadas antes de borrar
        affected_so_ids = set()
        for record in self:
            if record.so_id:
                affected_so_ids.add(record.so_id.id)

        #Realizamos el borrado real de la base de datos
        res = super(SOAttachment, self).unlink()

        #Re-secuenciamos los anexos restantes
        for so_id in affected_so_ids:
            remaining_attachments = self.search([
                ('so_id', '=', so_id)
            ], order='sequence_number asc')
            
            for index, attach in enumerate(remaining_attachments, start=1):
                if attach.sequence_number != index:
                    attach.write({'sequence_number': index})
                
        return res


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    #Solo inyectamos la relación One2many hacia el nuevo modelo
    attachments = fields.One2many("sale.order.attachment", "so_id", string="Guías Adjuntas")