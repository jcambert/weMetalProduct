# -*- coding: utf-8 -*-
from odoo import models, fields, api,_,tools
from odoo.exceptions import AccessError, UserError,ValidationError
from .models import Model,SHEETMETAL_CATEGORY
from ast import literal_eval
import logging
import re
import math
_logger = logging.getLogger(__name__)

class WeProductCategory(Model):
    
    _inherit='product.category'
    surface_formula=fields.Char('Surface Formula')
    volume_formula=fields.Char('Volume Formula')
    weight_formula=fields.Char('Weight Formula')
    convention=fields.Char('Convention',help="python regex string convention")
    
    @api.model
    def parse(self,convention,value,results):
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(value)
        if m:
            if isinstance(results,dict):
                results.update(m.groupdict())
            return True
        return False
class WeProductTemplate(Model):
    _inherit = ['product.template']
    _description = 'Product Metal Template'
    _sql_constraints = [
        ('we_product_name_uniq','unique(name)',"This name already exist !")
    ]

    

    # product_type=fields.Selection([('none','Aucun'),('sheetmetal','Tole'),('tuberond','Tube Rond'),('tubecarre','Tube Carré'),('tuberect','Tube Rect.'),('profile','Profilé')],string='Type')
    # indices=fields.One2many('we.indice','product',string="Indice")
    # current_indice = fields.Char('Current indice',compute='_compute_current_indice',readonly=True)
    state = fields.Selection(
        [('draft','Draft'),('running','running'),('closed','Closed')],
        string='State',
        default='draft',
        copy=False,required=True,help="Statut",tracking=True,store=True)
    material = fields.Many2one('we.material','Material')
    finition = fields.Char('Finition',default='')


    # profile_type=fields.Many2one('we.profile.type')
    is_profile=fields.Boolean('Profile',readonly =True)
    is_sheetmetal =fields.Boolean('Sheetmetal',readonly =True)
    # is_predefined_profile=fields.Boolean('Is predefined profile')
    # profile_length = fields.Integer('Profile length')
    # surface_section = fields.Float('Surface Section', digits='Product Unit of Measure', default=0.0)
    # surface_meter = fields.Float('Surface per meter', digits='Product Unit of Measure', default=0.0)
    # weight_meter = fields.Float('Weight per meter', digits='Product  Unit of Measure', default=0.0)

    surface=fields.Float('Surface',store=True,compute='_compute_material_values', digits='Product Unit of Measure',default=0.0)
    weight=fields.Float('Weight',store=True,compute='_compute_material_values', digits='Product Unit of Measure',default=0.0)

    linear_weight=fields.Float('Linear weight',compute='_compute_linear_weight',help='Weight per base unit length')
    length=fields.Float('Length',digits='Product Unit of Measure',default=0.0,help="Length for sheetmetal or profile or pipe")
    width=fields.Float('Width',digits='Product Unit of Measure',default=0.0,help="Width for sheetmetal or rect/square pipe ")#Width | external diameter
    height=fields.Float('Height',digits='Product Unit of Measure',default=0.0,help="Height for rect/square pipe or External diameter")#length | external diameter
    # dim3=fields.Float('dim3',digits='Product Unit of Measure',default=0.0)#Length, internal diameter
    # dim4=fields.Float('dim4',digits='Product Unit of Measure',default=0.0)#Width, internal diameter
    thickness=fields.Float('Thickness',digits='Product Unit of Measure',default=0.0,help="Thickness for Sheetmetal and Pipe")#thickness

    
    @api.onchange('name')
    def set_upper(self):    
        if isinstance(self.name,str):
            force=self.env['ir.config_parameter'].get_param('weMetalProduct.product_name_force_uppercase')
            self.name = str(self.name).upper() if force else str(self.name)
        return


    # @api.depends('indices.is_enable')
    def _compute_current_indice(self):
        def get_last_indice(record):
            return record.indices.filtered(lambda i:i.is_enable)
            
        for record in self:
            indice = get_last_indice(record)
            record.current_indice= indice.name() if indice.exists() else ''

    def _filterByRe(self,*args):
        if len(args) not in [2,3]:
            return False
        convention,name,res=args[0],args[1],args[2] if len(args)==3 else None
        if(not convention or not name or len(convention)==0 or len(name)==0):
            return False
        _logger.info(f"Filtering: Convention->{convention} , name->{name}")
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(name)
        if m:
            if isinstance(res,dict):
                res.update(m.groupdict())
            return True
        return False
    

    
    

    def parse(self,convention,value,results):
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(value)
        if m:
            if isinstance(results,dict):
                results.update(m.groupdict())
            return True
        return False
    @api.onchange('categ_id','name')
    def _compute_type(self):
        materials=self.env['we.material'].search([])
        try:
            record=self
            record.is_profile=False
            record.is_sheetmetal=True
            if not record.categ_id or not record.name:
                return
            groups={}
            categ=record.categ_id
            # print(record.name)
            # print(categ.convention)
            if not categ.convention or not self.parse(categ.convention,record.name,groups):
                return
            
            if 'material' in groups:
                material=materials.filtered(lambda r:self._filterByRe(r.convention,groups['material']))
                if material.exists() :
                    self.material=material[0]
            else:
                material=materials.filtered(lambda r:r.default)
                if material.exists()    :
                    self.material=material[0]
            if 'length' in groups:
                self.length=float(groups['length'])
            if 'width' in groups:
                self.width=float(groups['width'])
            if 'height' in groups:
                self.weight=float(groups['height'])
            if 'thickness' in groups:
                self.thickness=float(groups['thickness'])
            if 'finition' in groups:
                self.finition=groups['finition']
        except:
            pass
        
    @api.onchange('weight')            
    def _compute_linear_weight(self):
        for record in self:
            #TODO Compute weight per meter usin uom
            record.linear_weight=0.0

    @api.onchange('length','width','height','thickness','material')
    def _compute_weight(self):
        for record in self:
            if len(record.product_variant_ids)==1:
                length,width,height,thickness,volmass=record.length,record.width,record.height,record.thickness,record.material.volmass
                w_formula=record.categ_id.weight_formula
                w_code=compile(w_formula, "<string>", "eval")
                record.weight=float(eval(w_code))
    
    # @api.constrains('dim2')
    def _check_sheetmetal_width(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.dim2<=0:
                raise ValidationError(_('Sheetmetal width must be greater than 0'))

    # @api.constrains('dim1')
    def _check_sheetmetal_length(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.dim1<=0:
                raise ValidationError(_('Sheetmetal length must be greater than 0'))
            
    # @api.constrains('dim5')
    def _check_sheetmetal_thickness(self):
        if any( record.is_sheetmetal and record.dim5<=0 for record in self):
            raise ValidationError(_('Sheetmetal thickness must be greater than 0'))
        #thickness profile can be 0 

    
            


    # def action_view_indice(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("weMetalProduct.we_indice_action")
    #     action['domain'] = [ ('product', 'in', self.ids)]
    #     action['context'] = {}
    #     return action

class WeProductProduct(Model):
    _inherit = 'product.product'
    _description = 'Product Metal'
    # product_type=fields.Selection(related='product_tmpl_id.product_type',string='Type',store=False)
    length=fields.Float(compute='_compute_size',store=True)
    width=fields.Float(compute='_compute_size',store=True)
    thickness=fields.Float(related='product_tmpl_id.thickness',string='Thickness',store=True)
    material= fields.Many2one('we.material',related='product_tmpl_id.material')
    
    @api.depends('product_template_attribute_value_ids','product_tmpl_id.name','product_tmpl_id.categ_id')
    def _compute_size(self):
        for product in self:
            # indices = product.product_template_attribute_value_ids._ids2str()
            # print(product.product_template_attribute_value_ids.attribute_id)
            # print(product.product_template_attribute_value_ids.product_attribute_value_id)
            if product.product_template_attribute_value_ids.attribute_id.display_type=='sheetmetalsize':
                product.default_code=product.product_tmpl_id.name + product.product_template_attribute_value_ids.product_attribute_value_id.code_suffixe
                product.length=product.product_template_attribute_value_ids.product_attribute_value_id.length
                product.width=product.product_template_attribute_value_ids.product_attribute_value_id.width
                length,width,thickness,volmass=product.length,product.width,product.thickness,product.material.volmass
                s_formula, v_formula, w_formula=product.categ_id.surface_formula,product.categ_id.volume_formula,product.categ_id.weight_formula
                s_code=compile(s_formula, "<string>", "eval")
                v_code=compile(v_formula, "<string>", "eval")
                w_code=compile(w_formula, "<string>", "eval")
                product.surface,product.volume, product.weight=float(eval(s_code)),float(eval(v_code)),float(eval(w_code))
            elif product.product_template_attribute_value_ids.attribute_id.display_type=='profilelength':
                product.default_code=product.product_tmpl_id.name + product.product_template_attribute_value_ids.product_attribute_value_id.code_suffixe
                product.length=product.product_template_attribute_value_ids.product_attribute_value_id.length
                product.width=product.product_tmpl_id.width
                length,width,height,thickness,volmass=product.length,product.width,product.height,product.thickness,product.material.volmass
                w_formula=product.categ_id.weight_formula
                if w_formula and len(w_formula)>0:
                    w_code=compile(w_formula, "<string>", "eval")
                    product.weight=float(eval(w_code))
            else:
                product.length=0.0