# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
from ast import literal_eval
import logging
import re
import math

class WeProfileType(models.Model):
    _name='we.profile.type'
    _description='Standard Profile Type' #UPN HEA ..
    _inherit=['we.convention']
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Name',required=True)
    product_type=fields.Selection([('none','Aucun'),('sheetmetal','Tole'),('tuberond','Tube Rond'),('tubecarre','Tube Carré'),('tuberect','Tube Rect.'),('profile','Profilé')],string='Type')
    length=fields.Float('Length',default=0.0)
    width=fields.Float('Width',default=0.0)
    default_length=fields.Integer('Default length',default=0.0)
    # convention=fields.Char('Convention',required=True,help="python regex string convention")
    calculate_surface_section=fields.Char('Surface section formula',default='')
    calculate_surface_meter=fields.Char('Surface meter formula',default='')
    calculate_dim2=fields.Char('Dimension 2 formula',default='')
    calculate_dim3=fields.Char('Dimension 3 formula',default='')
    calculate_dim4=fields.Char('Dimension 4 formula',default='')

    @api.onchange('calculate_surface_section')
    def _on_change_calculate_surface_section(self):
        for record in self.filtered(lambda r:isinstance(r.calculate_surface_section,str)):
            record.calculate_surface_section=record.calculate_surface_section.strip()
    @api.onchange('calculate_surface_meter')
    def _on_change_calculate_surface_meter(self):
        for record in self.filtered(lambda r:isinstance(r.calculate_surface_meter,str)):
            record.calculate_surface_meter=record.calculate_surface_meter.strip()
    @api.onchange('calculate_dim2')
    def _on_change_calculate_dim2(self):
        for record in self.filtered(lambda r:isinstance(r.calculate_dim2,str)):
            record.calculate_dim2=record.calculate_dim2.strip()
    @api.onchange('calculate_dim3')
    def _on_change_calculate_dim3(self):
        for record in self.filtered(lambda r:isinstance(r.calculate_dim3,str)):
            record.calculate_dim3=record.calculate_dim3.strip()
    @api.onchange('calculate_dim4')
    def _on_change_calculate_dim4(self):
        for record in self.filtered(lambda r:isinstance(r.calculate_dim4,str)):
            record.calculate_dim4=record.calculate_dim4.strip()
    
    

    # @api.constrains('calculate_surface_section')
    # def check_calculate_surface_section(self):
    #     for record in self.filtered(lambda r:isinstance(r.calculate_surface_section,str) and len(r.calculate_surface_section)>0):
    #         record.calculate_surface_section=record.calculate_surface_section.strip()
    # @api.constrains('calculate_surface_meter')
    # def check_calculate_surface_meter(self):
    #     for record in self.filtered(lambda r:isinstance(r.calculate_surface_meter,str) and len(r.calculate_surface_meter)>0):
    #         record.calculate_surface_meter=record.calculate_surface_meter.strip()
    # @api.constrains('calculate_dim2')
    # def check_calculate_dim2(self):
    #     for record in self.filtered(lambda r:isinstance(r.calculate_dim2,str) and len(r.dim2)>0):
    #         record.calculate_dim2=record.calculate_dim2.strip()
    # @api.constrains('calculate_dim3')
    # def check_calculate_dim3(self):
    #     for record in self.filtered(lambda r:isinstance(r.calculate_dim3,str) and len(r.dim3)>0):
    #         record.calculate_dim3=record.calculate_dim3.strip()
    # @api.constrains('calculate_dim4')
    # def check_calculate_dim4(self):
    #     for record in self.filtered(lambda r:isinstance(r.calculate_dim4,str) and len(r.dim4)>0):
    #         record.calculate_dim4=record.calculate_dim4.strip()

class WeProfile(models.Model):
    _name='we.profile'
    _description='Standard Profile Dimension'
    _sql_constraints = [
        ('we_profile_name_uniq','unique(type_id,name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Name',required=True,index=True)
    type_id=fields.Many2one('we.profile.type','Type',required=True)
    surface_section=fields.Float('Surface',default=0.0)
    surface_meter=fields.Float('Surface meter',default=0.0)
    weight_meter=fields.Float('Weight meter',default=0.0)