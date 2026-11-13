from django import forms
from .models import RepuestoGenerico, Neumatico, Llanta, ProductoBase, CategoriaProducto, MovimientoStock


WIDGET_DEFAULTS = {'class': 'form-input'}


class RepuestoForm(forms.ModelForm):
    # ProductoBase fields
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.filter(tipo='REPUESTO'),
        widget=forms.Select(attrs=WIDGET_DEFAULTS), label='Categoria'
    )
    codigo_sku = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Autogenerable (Ej: FRE-BREMBO-001)'}), label='Codigo SKU', help_text='Dejar vacío para generar automáticamente según [FAMILIA]-[SUBFAMILIA]-[CORRELATIVO]')
    nombre = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Nombre del repuesto'}), label='Nombre')
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2}), label='Descripcion')
    precio_costo = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de costo')
    precio_venta = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de venta')
    stock_actual = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock actual', initial=0)
    stock_minimo = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock minimo', initial=5)
    aplicacion = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Marcas/Modelos compatibles (ej: Toyota, Nissan 2018-2023)'}), label='Compatibilidad vehicular / Aplicación')
    es_adaptable = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='Es adaptable')
    notas_adaptacion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2, 'placeholder': 'Detalles de modificaciones o adaptación requerida'}), label='Notas de adaptación')
    imagen = forms.ImageField(required=False, widget=forms.FileInput(attrs=WIDGET_DEFAULTS), label='Imagen')
    class Meta:
        model = RepuestoGenerico
        fields = ['marca_repuesto', 'numero_parte', 'compatible_con']
        widgets = {
            'marca_repuesto': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Marca del repuesto'}),
            'numero_parte': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Numero de parte'}),
            'compatible_con': forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2, 'placeholder': 'Toyota Corolla 2015-2022...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pb = self.instance.producto
            self.fields['categoria'].initial = pb.categoria
            self.fields['codigo_sku'].initial = pb.codigo_sku
            self.fields['nombre'].initial = pb.nombre
            self.fields['descripcion'].initial = pb.descripcion
            self.fields['precio_costo'].initial = pb.precio_costo
            self.fields['precio_venta'].initial = pb.precio_venta
            self.fields['stock_actual'].initial = pb.stock_actual
            self.fields['stock_minimo'].initial = pb.stock_minimo
            self.fields['aplicacion'].initial = pb.aplicacion
            self.fields['es_adaptable'].initial = pb.es_adaptable
            self.fields['notas_adaptacion'].initial = pb.notas_adaptacion

    def clean_codigo_sku(self):
        sku = self.cleaned_data.get('codigo_sku', '').strip().upper()
        if not sku or sku.endswith('-'):
            return ''
        qs = ProductoBase.objects.filter(codigo_sku=sku)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.producto.pk)
        if qs.exists():
            raise forms.ValidationError(f'El código SKU "{sku}" ya está registrado por otro producto.')
        return sku

    def save(self, commit=True, usuario=''):
        categoria = self.cleaned_data['categoria']
        sku = self.cleaned_data.get('codigo_sku', '').strip().upper()
        
        # Generación automática estricta según [FAMILIA]-[SUBFAMILIA/ESPECIFICACIÓN]-[CORRELATIVO]
        if not sku or sku.endswith('-'):
            prefijo = 'REP'
            if categoria and getattr(categoria, 'codigo_prefijo', None):
                prefijo = categoria.codigo_prefijo.strip().upper()
            
            marca = (self.cleaned_data.get('marca_repuesto') or '').strip().upper()
            import re
            subfamilia = re.sub(r'[^A-Z0-9]', '', marca)[:8] if marca else 'GEN'
            base_patron = f"{prefijo}-{subfamilia}-"

            existentes = ProductoBase.objects.filter(codigo_sku__startswith=base_patron).values_list('codigo_sku', flat=True)
            max_num = 0
            for s in existentes:
                partes = s.split('-')
                if partes and partes[-1].isdigit():
                    num = int(partes[-1])
                    if num > max_num:
                        max_num = num
            sku = f"{base_patron}{str(max_num + 1).zfill(3)}"

        # Save ProductoBase first
        pb_data = {
            'categoria': categoria,
            'codigo_sku': sku,
            'nombre': self.cleaned_data['nombre'],
            'descripcion': self.cleaned_data.get('descripcion', ''),
            'precio_costo': self.cleaned_data['precio_costo'],
            'precio_venta': self.cleaned_data['precio_venta'],
            'stock_actual': self.cleaned_data['stock_actual'],
            'stock_minimo': self.cleaned_data['stock_minimo'],
            'aplicacion': self.cleaned_data.get('aplicacion', ''),
            'es_adaptable': self.cleaned_data.get('es_adaptable', False),
            'notas_adaptacion': self.cleaned_data.get('notas_adaptacion', ''),
            'tipo_producto': 'REPUESTO',
        }
        if self.cleaned_data.get('imagen'):
            pb_data['imagen'] = self.cleaned_data['imagen']

        if self.instance.pk:
            pb = self.instance.producto
            stock_anterior = pb.stock_actual
            for k, v in pb_data.items():
                setattr(pb, k, v)
            pb.save()
            
            # Detectar cambio manual de stock en edicion
            if pb.stock_actual != stock_anterior:
                from .models import MovimientoStock
                diff = pb.stock_actual - stock_anterior
                MovimientoStock.objects.create(
                    producto=pb,
                    tipo_movimiento='ENTRADA' if diff > 0 else 'SALIDA',
                    cantidad=diff,
                    stock_resultante=pb.stock_actual,
                    motivo='Ajuste manual desde edición de repuesto',
                    precio_unitario=pb.precio_costo,
                    usuario=usuario or 'Sistema'
                )
            is_new = False
        else:
            pb = ProductoBase.objects.create(**pb_data)
            is_new = True

        repuesto = super().save(commit=False)
        repuesto.producto = pb
        if commit:
            repuesto.save()
            if is_new and pb.stock_actual > 0:
                from .models import MovimientoStock
                MovimientoStock.objects.create(
                    producto=pb, tipo_movimiento='ENTRADA',
                    cantidad=pb.stock_actual, stock_resultante=pb.stock_actual,
                    motivo='Carga inicial de inventario',
                    precio_unitario=pb.precio_costo,
                    usuario=usuario or 'Sistema'
                )
        return repuesto


class NeumaticoForm(forms.ModelForm):
    # ProductoBase fields
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.filter(tipo='NEUMATICO'),
        widget=forms.Select(attrs=WIDGET_DEFAULTS), label='Categoria',
        required=False
    )
    codigo_sku = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Autogenerable (Ej: NEU-20555R16-AT-001)'}), label='Codigo SKU', help_text='Dejar vacío para generar automáticamente según [FAMILIA]-[MEDIDA/TIPO]-[CORRELATIVO]')
    nombre = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Nombre del neumatico'}), label='Nombre')
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2}), label='Descripcion')
    precio_costo = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de costo')
    precio_venta = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de venta')
    stock_actual = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock actual', initial=0)
    stock_minimo = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock minimo', initial=5)
    aplicacion = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Marcas/Modelos compatibles (ej: Toyota, Nissan 2018-2023)'}), label='Compatibilidad vehicular / Aplicación')
    es_adaptable = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='Es adaptable')
    notas_adaptacion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2, 'placeholder': 'Detalles de modificaciones o adaptación requerida'}), label='Notas de adaptación')
    imagen = forms.ImageField(required=False, widget=forms.FileInput(attrs=WIDGET_DEFAULTS), label='Imagen')
    class Meta:
        model = Neumatico
        fields = ['marca_neumatico', 'modelo_neumatico', 'ancho', 'perfil', 'diametro', 'indice_carga', 'indice_velocidad', 'tipo', 'estado', 'profundidad_restante']
        widgets = {
            'marca_neumatico': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Michelin, Bridgestone...'}),
            'modelo_neumatico': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Modelo'}),
            'ancho': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '195', 'min': '100', 'max': '400'}),
            'perfil': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '65', 'min': '25', 'max': '95'}),
            'diametro': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '15', 'min': '12', 'max': '24'}),
            'indice_carga': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '91'}),
            'indice_velocidad': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'H'}),
            'tipo': forms.Select(attrs=WIDGET_DEFAULTS),
            'estado': forms.Select(attrs=WIDGET_DEFAULTS),
            'profundidad_restante': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.1', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pb = self.instance.producto
            self.fields['categoria'].initial = pb.categoria
            self.fields['codigo_sku'].initial = pb.codigo_sku
            self.fields['nombre'].initial = pb.nombre
            self.fields['descripcion'].initial = pb.descripcion
            self.fields['precio_costo'].initial = pb.precio_costo
            self.fields['precio_venta'].initial = pb.precio_venta
            self.fields['stock_actual'].initial = pb.stock_actual
            self.fields['stock_minimo'].initial = pb.stock_minimo
            self.fields['aplicacion'].initial = pb.aplicacion
            self.fields['es_adaptable'].initial = pb.es_adaptable
            self.fields['notas_adaptacion'].initial = pb.notas_adaptacion

    def clean_codigo_sku(self):
        sku = self.cleaned_data.get('codigo_sku', '').strip().upper()
        if not sku or sku.endswith('-'):
            return ''
        qs = ProductoBase.objects.filter(codigo_sku=sku)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.producto.pk)
        if qs.exists():
            raise forms.ValidationError(f'El código SKU "{sku}" ya está registrado por otro producto.')
        return sku

    def save(self, commit=True, usuario=''):
        categoria = self.cleaned_data.get('categoria')
        if not categoria:
            categoria, _ = CategoriaProducto.objects.get_or_create(
                nombre='Neumáticos Turismo',
                defaults={'codigo_prefijo': 'NEU', 'tipo': 'NEUMATICO', 'descripcion': 'Neumáticos de turismo y carga'}
            )

        sku = self.cleaned_data.get('codigo_sku', '').strip().upper()
        if not sku or sku.endswith('-'):
            prefijo = 'NEU'
            if categoria and getattr(categoria, 'codigo_prefijo', None):
                prefijo = categoria.codigo_prefijo.strip().upper()
            ancho = self.cleaned_data.get('ancho') or 0
            perfil = self.cleaned_data.get('perfil') or 0
            diametro = self.cleaned_data.get('diametro') or 0
            tipo = (self.cleaned_data.get('tipo') or 'ALL_SEASON').upper()
            sub = f"{ancho}{perfil}R{diametro}-{tipo}"
            base_patron = f"{prefijo}-{sub}-"
            
            existentes = ProductoBase.objects.filter(codigo_sku__startswith=base_patron).values_list('codigo_sku', flat=True)
            max_num = 0
            for s in existentes:
                partes = s.split('-')
                if partes and partes[-1].isdigit():
                    num = int(partes[-1])
                    if num > max_num:
                        max_num = num
            sku = f"{base_patron}{str(max_num + 1).zfill(3)}"

        pb_data = {
            'categoria': categoria,
            'codigo_sku': sku,
            'nombre': self.cleaned_data['nombre'],
            'descripcion': self.cleaned_data.get('descripcion', ''),
            'precio_costo': self.cleaned_data['precio_costo'],
            'precio_venta': self.cleaned_data['precio_venta'],
            'stock_actual': self.cleaned_data['stock_actual'],
            'stock_minimo': self.cleaned_data['stock_minimo'],
            'aplicacion': self.cleaned_data.get('aplicacion', ''),
            'es_adaptable': self.cleaned_data.get('es_adaptable', False),
            'notas_adaptacion': self.cleaned_data.get('notas_adaptacion', ''),
            'tipo_producto': 'NEUMATICO',
        }
        if self.cleaned_data.get('imagen'):
            pb_data['imagen'] = self.cleaned_data['imagen']

        if self.instance.pk:
            pb = self.instance.producto
            stock_anterior = pb.stock_actual
            for k, v in pb_data.items():
                setattr(pb, k, v)
            pb.save()

            # Detectar cambio manual de stock en edicion
            if pb.stock_actual != stock_anterior:
                from .models import MovimientoStock
                diff = pb.stock_actual - stock_anterior
                MovimientoStock.objects.create(
                    producto=pb,
                    tipo_movimiento='ENTRADA' if diff > 0 else 'SALIDA',
                    cantidad=diff,
                    stock_resultante=pb.stock_actual,
                    motivo='Ajuste manual desde edición de neumático',
                    precio_unitario=pb.precio_costo,
                    usuario=usuario or 'Sistema'
                )
            is_new = False
        else:
            pb = ProductoBase.objects.create(**pb_data)
            is_new = True

        neumatico = super().save(commit=False)
        neumatico.producto = pb
        if commit:
            neumatico.save()
            if is_new and pb.stock_actual > 0:
                from .models import MovimientoStock
                MovimientoStock.objects.create(
                    producto=pb, tipo_movimiento='ENTRADA',
                    cantidad=pb.stock_actual, stock_resultante=pb.stock_actual,
                    motivo='Carga inicial de inventario (Neumático)',
                    precio_unitario=pb.precio_costo,
                    usuario=usuario or 'Sistema'
                )
        return neumatico


class LlantaForm(forms.ModelForm):
    # ProductoBase fields
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.filter(tipo__in=['LLANTA', 'REPUESTO']),
        widget=forms.Select(attrs=WIDGET_DEFAULTS), label='Categoría', required=False
    )
    codigo_sku = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Autogenerado (Ej: LLA-17IN-ALU-001)'}), label='Código SKU', help_text='Dejar vacío para generar automáticamente según formato LLA-[ESPECIFICACIÓN]-[CORRELATIVO]')
    nombre = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Nombre comercial de la llanta (ej: Llanta Deportiva R17)'}), label='Nombre')
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2}), label='Descripción')
    precio_costo = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de costo (Bs)')
    precio_venta = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de venta (Bs)')
    stock_actual = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock actual', initial=0)
    stock_minimo = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock mínimo', initial=4)
    aplicacion = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Vehículos compatibles (ej: Toyota Hilux, Ford Ranger, VW Gol)'}), label='Compatibilidad vehicular / Aplicación')
    es_adaptable = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='Es adaptable')
    notas_adaptacion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2, 'placeholder': 'Espaciadores, centradores o tornillería requerida'}), label='Notas de adaptación')
    imagen = forms.ImageField(required=False, widget=forms.FileInput(attrs=WIDGET_DEFAULTS), label='Fotografía de la Llanta')

    class Meta:
        model = Llanta
        fields = ['marca_llanta', 'subfamilia', 'rin', 'ancho_pulgadas', 'apernadura', 'offset_et', 'centro_cb', 'color']
        widgets = {
            'marca_llanta': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Ej: Enkei, BBS, Ronal, Original...'}),
            'subfamilia': forms.Select(attrs=WIDGET_DEFAULTS),
            'rin': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '17', 'min': '10', 'max': '30'}),
            'ancho_pulgadas': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '7.5', 'step': '0.5'}),
            'apernadura': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '5x114.3 o 4x100'}),
            'offset_et': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '38'}),
            'centro_cb': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': '67.1', 'step': '0.1'}),
            'color': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Negro Mate, Gris Grafito, Diamantado...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pb = self.instance.producto
            self.fields['categoria'].initial = pb.categoria
            self.fields['codigo_sku'].initial = pb.codigo_sku
            self.fields['nombre'].initial = pb.nombre
            self.fields['descripcion'].initial = pb.descripcion
            self.fields['precio_costo'].initial = pb.precio_costo
            self.fields['precio_venta'].initial = pb.precio_venta
            self.fields['stock_actual'].initial = pb.stock_actual
            self.fields['stock_minimo'].initial = pb.stock_minimo
            self.fields['aplicacion'].initial = pb.aplicacion
            self.fields['es_adaptable'].initial = pb.es_adaptable
            self.fields['notas_adaptacion'].initial = pb.notas_adaptacion

    def clean_codigo_sku(self):
        sku = self.cleaned_data.get('codigo_sku', '').strip().upper()
        if not sku or sku.endswith('-'):
            return ''
        qs = ProductoBase.objects.filter(codigo_sku=sku)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.producto.pk)
        if qs.exists():
            raise forms.ValidationError(f'El código SKU "{sku}" ya está registrado por otro producto.')
        return sku

    def save(self, commit=True, usuario=''):
        categoria = self.cleaned_data.get('categoria')
        if not categoria:
            categoria, _ = CategoriaProducto.objects.get_or_create(
                nombre='Llantas y Rines',
                defaults={'codigo_prefijo': 'LLA', 'tipo': 'LLANTA', 'descripcion': 'Llantas de aleación y acero'}
            )

        sku = self.cleaned_data.get('codigo_sku', '').strip().upper()
        if not sku or sku.endswith('-'):
            prefijo = 'LLA'
            if categoria and getattr(categoria, 'codigo_prefijo', None):
                prefijo = categoria.codigo_prefijo.strip().upper()
            rin = self.cleaned_data.get('rin') or 0
            subfam = (self.cleaned_data.get('subfamilia') or 'ALU').upper()
            import re
            apernadura = re.sub(r'[^A-Z0-9]', '', (self.cleaned_data.get('apernadura') or '').upper()) or 'STD'
            sub = f"{rin}IN-{subfam}-{apernadura}"
            base_patron = f"{prefijo}-{sub}-"
            
            existentes = ProductoBase.objects.filter(codigo_sku__startswith=base_patron).values_list('codigo_sku', flat=True)
            max_num = 0
            for s in existentes:
                partes = s.split('-')
                if partes and partes[-1].isdigit():
                    num = int(partes[-1])
                    if num > max_num:
                        max_num = num
            sku = f"{base_patron}{str(max_num + 1).zfill(3)}"

        pb_data = {
            'categoria': categoria,
            'codigo_sku': sku,
            'nombre': self.cleaned_data['nombre'],
            'descripcion': self.cleaned_data.get('descripcion', ''),
            'precio_costo': self.cleaned_data['precio_costo'],
            'precio_venta': self.cleaned_data['precio_venta'],
            'stock_actual': self.cleaned_data['stock_actual'],
            'stock_minimo': self.cleaned_data['stock_minimo'],
            'aplicacion': self.cleaned_data.get('aplicacion', ''),
            'es_adaptable': self.cleaned_data.get('es_adaptable', False),
            'notas_adaptacion': self.cleaned_data.get('notas_adaptacion', ''),
            'tipo_producto': 'LLANTA',
        }
        if self.cleaned_data.get('imagen'):
            pb_data['imagen'] = self.cleaned_data['imagen']

        if self.instance.pk:
            pb = self.instance.producto
            stock_anterior = pb.stock_actual
            for k, v in pb_data.items():
                setattr(pb, k, v)
            pb.save()

            if pb.stock_actual != stock_anterior:
                diff = pb.stock_actual - stock_anterior
                MovimientoStock.objects.create(
                    producto=pb,
                    tipo_movimiento='ENTRADA' if diff > 0 else 'SALIDA',
                    cantidad=diff,
                    stock_resultante=pb.stock_actual,
                    motivo='Ajuste manual desde edición de llanta',
                    precio_unitario=pb.precio_costo,
                    usuario=usuario or 'Sistema'
                )
            is_new = False
        else:
            pb = ProductoBase.objects.create(**pb_data)
            is_new = True

        llanta = super().save(commit=False)
        llanta.producto = pb
        if commit:
            llanta.save()
            # Si no tenia sku explicito, recalcular con los datos de llanta guardados
            if not pb.codigo_sku or pb.codigo_sku.startswith('LLA-0') or pb.codigo_sku.startswith('REP-'):
                pb.save()
            if is_new and pb.stock_actual > 0:
                MovimientoStock.objects.create(
                    producto=pb, tipo_movimiento='ENTRADA',
                    cantidad=pb.stock_actual, stock_resultante=pb.stock_actual,
                    motivo='Carga inicial de inventario (Llanta)',
                    precio_unitario=pb.precio_costo,
                    usuario=usuario or 'Sistema'
                )
        return llanta


class MovimientoStockForm(forms.Form):
    tipo_movimiento = forms.ChoiceField(
        choices=[('ENTRADA', 'Entrada de stock'), ('SALIDA', 'Salida de stock'), ('AJUSTE', 'Ajuste')],
        widget=forms.Select(attrs=WIDGET_DEFAULTS), label='Tipo de movimiento'
    )
    cantidad = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '1'}), label='Cantidad')
    motivo = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Motivo del movimiento'}), label='Motivo')


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'codigo_prefijo', 'tipo', 'descripcion', 'icono']
        widgets = {
            'nombre': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Nombre de la categoría (ej: Frenos)'}),
            'codigo_prefijo': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Prefijo (ej: FIL, FRE, LUB, MOT)', 'style': 'text-transform: uppercase;'}),
            'tipo': forms.Select(attrs=WIDGET_DEFAULTS),
            'descripcion': forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2, 'placeholder': 'Breve descripción...'}),
            'icono': forms.HiddenInput(),
        }
