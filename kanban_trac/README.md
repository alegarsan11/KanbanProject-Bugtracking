# Launch the proyect like this (ADMIN ADMIN) python3.11 is working only
tracd --port 8080 --basic-auth="*,.htpasswd,trac" proyectotrac/ otro_proyect/
# Configuración del Entorno de Trac y Personalización Frontend

Este documento detalla los pasos seguidos para configurar tipos de campos personalizados, organizar el flujo de trabajo mediante tipos propios (`defect`, `code`, `enhancement`) y realizar una personalización frontend ligera mediante JavaScript nativo para gestionar la visibilidad de los campos sin depender de plugins de terceros frágiles.

---

## 1. Dependencias del Entorno (`requirements.txt`)
Trac se gestiona a través de paquetes de Python estándar. El núcleo del sistema base y sus dependencias de entorno se declaran de la siguiente forma:

- **Trac**: Motor principal de seguimiento de incidencias.
- Base de datos soportada de forma nativa (SQLite para desarrollo o PostgreSQL para producción).

---

## 2. Definición de Tipos de Tickets Personalizados
Los tipos de tickets (`defect`, `code`, `enhancement`) se gestionan de forma nativa desde la interfaz de administración de Trac en la sección **Manage Ticket Types**, quedando registrados directamente en la base de datos del entorno.

---

## 3. Configuración de Campos Personalizados (`trac.ini`)
Los campos adicionales se configuran en el archivo `trac.ini` dentro de la sección `[ticket-custom]`. Por ejemplo:

```ini
[ticket-custom]
blockedby = text
blockedby.label = Blocked By

blocking = text
blocking.label = Blocking

cliente = text
cliente.label = Cliente / Empresa

feat_mockup = text
feat_mockup.label = Enlace a Mockup / Diseño

prioridad_cliente = select
prioridad_cliente.label = Urgencia del Cliente
prioridad_cliente.options = Baja | Media | Alta | Crítica
prioridad_cliente.value = Media

requiere_factura = checkbox
requiere_factura.label = Requiere Factura Oficial
requiere_factura.value = 0

notas_internas = textarea
notas_internas.label = Notas Internas
notas_internas.cols = 40
notas_internas.rows = 5
```

---

## 4. Inyección de JavaScript Personalizado (`site.js`) y Plantillas
Para evitar plugins de terceros obsoletos en Trac, se implementó una solución frontend nativa utilizando la carpeta `htdocs` y una plantilla de cabecera.

### A. Ubicación del Script (`htdocs/site.js`)
Se creó el archivo `site.js` dentro de la carpeta `htdocs` del entorno de Trac para manipular dinámicamente el DOM según la selección del tipo de ticket:

```javascript
jQuery(document).ready(function($) {
    function toggleCustomFields() {
        // Capturamos el tipo de ticket seleccionado mediante el ID nativo #type
        var tipoSeleccionado = $('#field-type').val();
        
        // Localizamos el contenedor del campo personalizado feat_mockup
        var $campoMockup = $('#field-feat_mockup, [name="field_feat_mockup"]').closest('tr, .field, div.field');
        
        // Ejemplo de regla condicional: Mostrar solo si el tipo es 'code'
        if (tipoSeleccionado === 'code') {
            $campoMockup.show();
        } else {
            $campoMockup.hide();
        }
    }
    
    // Ejecutar al cargar la página y ante cualquier cambio en el selector
    toggleCustomFields();
    
    $(document).on('change', '#field-type', function() {
        toggleCustomFields();
    });
});
```

### B. Enlace en Plantillas (`templates/site_head.html`)
Para forzar a Trac a cargar el archivo estático en las vistas de tickets, se creó una carpeta `templates` en el entorno con un archivo `site_head.html`:

```html
<script type="text/javascript" src="${href.chrome('site/site.js')}"></script>
```

## Troubleshooting: Sincronización Trac, Gitea y Repositorios Git

### 1. Error de "Changeset" o saltos extraños en Trac (Fechas de hace 57 años)

Si tras realizar cambios externos, inyecciones de datos o sincronizaciones con Gitea, Trac muestra errores al acceder a los commits o aparecen fechas anómalas (como el año 1970 / hace 57 años), se debe a una **desincronización en la caché de revisiones** o marcas de tiempo (`timestamps`) nulas en la base de datos (`trac.db`).

#### Solución Recomendada (Resync)
No es necesario eliminar registros de la base de datos a mano. Utiliza la herramienta de administración oficial de Trac para reindexar el repositorio:

```bash
trac-admin /ruta/a/tu/entorno/trac repository resync "nombre_del_repositorio"