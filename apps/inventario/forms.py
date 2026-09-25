from django import forms
from .models import RepuestoGenerico, Neumatico, ProductoBase, CategoriaProducto, MovimientoStock


WIDGET_DEFAULTS = {'class': 'form-input'}


class RepuestoForm(forms.ModelForm):
    # ProductoBase fields
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.filter(tipo='REPUESTO'),
        widget=forms.Select(attrs=WIDGET_DEFAULTS), label='Categoria'
    )
    codigo_sku = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Autogenerado (Ej: REP-001)'}), label='Codigo SKU', help_text='Dejar vacío para generar automáticamente')
    nombre = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Nombre del repuesto'}), label='Nombre')
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2}), label='Descripcion')
    precio_costo = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de costo')
    precio_venta = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de venta')
    stock_actual = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock actual', initial=0)
    stock_minimo = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock minimo', initial=5)
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

    def clean_codigo_sku(self):
        sku = self.cleaned_data.get('codigo_sku')
        qs = ProductoBase.objects.filter(codigo_sku=sku)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.producto.pk)
        if qs.exists():
            raise forms.ValidationError('Este código SKU ya está registrado por otro producto.')
        return sku

    def save(self, commit=True):
        # Save ProductoBase first
        pb_data = {
            'categoria': self.cleaned_data['categoria'],
            'codigo_sku': self.cleaned_data['codigo_sku'],
            'nombre': self.cleaned_data['nombre'],
            'descripcion': self.cleaned_data.get('descripcion', ''),
            'precio_costo': self.cleaned_data['precio_costo'],
            'precio_venta': self.cleaned_data['precio_venta'],
            'stock_actual': self.cleaned_data['stock_actual'],
            'stock_minimo': self.cleaned_data['stock_minimo'],
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
                    precio_unitario=pb.precio_costo
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
                    precio_unitario=pb.precio_costo
                )
        return repuesto


class NeumaticoForm(forms.ModelForm):
    # ProductoBase fields
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.filter(tipo='NEUMATICO'),
        widget=forms.Select(attrs=WIDGET_DEFAULTS), label='Categoria',
        required=False
    )
    codigo_sku = forms.CharField(required=False, widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Autogenerado (Ej: NEU-001)'}), label='Codigo SKU', help_text='Dejar vacío para generar automáticamente')
    nombre = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Nombre del neumatico'}), label='Nombre')
    descripcion = forms.CharField(required=False, widget=forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2}), label='Descripcion')
    precio_costo = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de costo')
    precio_venta = forms.DecimalField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'step': '0.01', 'min': '0'}), label='Precio de venta')
    stock_actual = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock actual', initial=0)
    stock_minimo = forms.IntegerField(widget=forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'min': '0'}), label='Stock minimo', initial=5)
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

    def clean_codigo_sku(self):
        sku = self.cleaned_data.get('codigo_sku')
        qs = ProductoBase.objects.filter(codigo_sku=sku)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.producto.pk)
        if qs.exists():
            raise forms.ValidationError('Este código SKU ya está registrado por otro producto.')
        return sku

    def save(self, commit=True):
        categoria = self.cleaned_data.get('categoria')
        if not categoria:
            categoria, _ = CategoriaProducto.objects.get_or_create(nombre='Neumaticos All Season', defaults={'descripcion': 'Neumaticos'})

        pb_data = {
            'categoria': categoria,
            'codigo_sku': self.cleaned_data['codigo_sku'],
            'nombre': self.cleaned_data['nombre'],
            'descripcion': self.cleaned_data.get('descripcion', ''),
            'precio_costo': self.cleaned_data['precio_costo'],
            'precio_venta': self.cleaned_data['precio_venta'],
            'stock_actual': self.cleaned_data['stock_actual'],
            'stock_minimo': self.cleaned_data['stock_minimo'],
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
                    precio_unitario=pb.precio_costo
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
                    precio_unitario=pb.precio_costo
                )
        return neumatico


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
        fields = ['nombre', 'tipo', 'descripcion', 'icono']
        widgets = {
            'nombre': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Nombre de la categoría'}),
            'tipo': forms.Select(attrs=WIDGET_DEFAULTS),
            'descripcion': forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2, 'placeholder': 'Breve descripción...'}),
            'icono': forms.HiddenInput(),
        }
