# E-commerce Platform

![Django Version](https://img.shields.io/badge/Django-5.2-green.svg)
![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Stripe](https://img.shields.io/badge/Payments-Stripe-purple.svg)


Una plataforma de comercio electrónico robusta, escalable y moderna desarrollada con Django y Django REST Framework. Este proyecto implementa funcionalidades esenciales para una tienda en línea, incluyendo gestión de productos, usuarios, carrito de compras, procesamiento de pagos con Stripe y más.

## Características

- **Sistema de Autenticación Personalizado**: Registro con verificación por correo, inicio de sesión, gestión de perfil
- **Gestión de Productos**: Categorización, búsqueda, y filtrado de productos
- **Carrito de Compras**: Persistente para usuarios registrados y anónimos
- **Pasarela de Pagos**: Integración completa con Stripe para pagos seguros
- **Gestión de Pedidos**: Seguimiento y administración de pedidos
- **Notificaciones por Correo**: Confirmaciones de pedidos y comunicaciones con clientes
- **Seguridad Robusta**: Protección CSRF, autenticación segura y más
- **Diseño Responsive**: Funciona en todos los dispositivos
- **API RESTful**: Endpoints completos para integración con aplicaciones frontend

## Arquitectura

El proyecto está estructurado en módulos específicos:

```
ecommerce/
├── apps/
│   ├── products/      # Gestión de productos y categorías
│   ├── custom_auth/   # Sistema de autenticación personalizado
│   ├── cart/          # Funcionalidad del carrito de compras
│   ├── payments/      # Integración con Stripe para pagos
│   ├── orders/        # Gestión de pedidos
│   └── mailer/        # Sistema de notificaciones por correo
├── templates/         # Plantillas HTML
├── static/            # Archivos estáticos (CSS, JS, imágenes)
├── media/             # Archivos multimedia subidos por usuarios
└── ecommerce/         # Configuración central del proyecto
```

## Diagrama Relacional

El siguiente diagrama muestra la estructura de la base de datos y las relaciones entre las diferentes entidades:

![Diagrama Relacional](https://github.com/user-attachments/assets/d05a5bd5-592c-407a-852f-39c9e6cfc16a)

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de Stripe para procesamiento de pagos
- Cuenta de correo electrónico para envío de notificaciones

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tuusuario/ecommerce_project.git
cd ecommerce_project
```

### Paso 2: Configurar el Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con la siguiente información:

```
SECRET_KEY=tu_clave_secreta_django
DEBUG=True
DATABASE_URL=postgres://usuario:contraseña@localhost:5432/nombre_db
STRIPE_PUBLIC_KEY=pk_test_tu_clave_publica_stripe
STRIPE_SECRET_KEY=sk_test_tu_clave_secreta_stripe
STRIPE_WEBHOOK_SECRET=whsec_tu_secreto_webhook_stripe
EMAIL_HOST_USER=tu_email@ejemplo.com
EMAIL_HOST_PASSWORD=tu_contraseña_email
```

### Paso 5: Aplicar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 6: Crear Superusuario

```bash
python manage.py createsuperuser
```

### Paso 7: Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

Ahora puedes acceder al proyecto en `http://localhost:8000/`

## Configuración Avanzada

### Stripe (Procesamiento de Pagos)

1. **Crea una cuenta en Stripe**:
   - Registra una cuenta en [Stripe](https://stripe.com)
   - Obtén tus claves API desde el panel de control

2. **Configura los Webhooks**:
   - En el panel de Stripe, crea un nuevo webhook
   - URL del endpoint: `https://tu-dominio.com/payments/webhook/`
   - Eventos a escuchar: `payment_intent.succeeded`, `payment_intent.payment_failed`

3. **Para pruebas de pagos**:
   - Usa las [tarjetas de prueba de Stripe](https://stripe.com/docs/testing#cards)
   - Ejemplo: `4242 4242 4242 4242` (fecha futura, cualquier CVC)

### SendGrid (Correo Electrónico)

1. **Configura SendGrid**:
   - Crea una cuenta en [SendGrid](https://sendgrid.com)
   - Obtén una API key

2. **Actualiza las configuraciones**:
   - Agrega las credenciales al archivo `.env`
   - Ajusta la configuración de correo en `settings.py`

### Base de Datos en Producción

Para usar PostgreSQL en producción:

1. Instala el paquete:
   ```bash
   pip install psycopg2-binary
   ```

2. Configura `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'nombre_db',
           'USER': 'usuario',
           'PASSWORD': 'contraseña',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

## Uso de la API

### Autenticación

```http
POST /custom_auth/register/
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "username": "usuario",
  "name": "Nombre",
  "last_name": "Apellido",
  "password": "contraseña",
  "confirm_password": "contraseña"
}
```

```http
POST /custom_auth/login/
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "contraseña"
}
```

### Productos

```http
GET /products/dashboard/
Authorization: Bearer {token}
```

```http
POST /products/add/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Producto Ejemplo",
  "description": "Descripción del producto",
  "price": 1999,
  "category": "ELECTRONICA",
  "stock": 10
}
```

### Carrito

```http
GET /cart/detail/
Authorization: Bearer {token}
```

```http
POST /cart/add/{product_id}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "quantity": 2
}
```

### Pagos

```http
POST /payments/checkout/
Authorization: Bearer {token}
Content-Type: application/json

{
  "shipping_address": "Dirección de envío completa",
  "contact_phone": "1234567890",
  "payment_method": "card"
}
```

## Flujo de Trabajo

1. **Registro de Usuario**:
   - El usuario se registra y recibe un correo de verificación
   - Confirma su correo haciendo clic en el enlace recibido

2. **Navegación y Compra**:
   - El usuario navega por el catálogo de productos
   - Agrega productos al carrito
   - Procede al checkout

3. **Proceso de Pago**:
   - Introduce información de envío
   - Realiza el pago con Stripe
   - Recibe confirmación del pedido

4. **Seguimiento de Pedidos**:
   - El usuario puede ver el historial de sus pedidos
   - Recibe actualizaciones sobre el estado de su pedido

## Pruebas

Para ejecutar las pruebas unitarias:

```bash
python manage.py test
```

## Despliegue en Producción

### Consideraciones para Producción

1. **Configuración de Seguridad**:
   - Establece `DEBUG=False` en producción
   - Configura correctamente `ALLOWED_HOSTS`
   - Usa HTTPS con un certificado válido

2. **Servir Archivos Estáticos**:
   - Ejecuta `python manage.py collectstatic`
   - Configura un servidor web como Nginx para servir archivos estáticos

3. **Servidor WSGI**:
   - Usa Gunicorn o uWSGI como servidor WSGI
   - Ejemplo: `gunicorn ecommerce.wsgi:application`

4. **Monitoreo**:
   - Implementa herramientas de monitoreo como Sentry o New Relic

## Contribución

Las contribuciones son bienvenidas! Si deseas contribuir:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

Por favor, asegúrate de seguir nuestras pautas de código y añadir pruebas unitarias para nuevas funcionalidades.

## Licencia

Este proyecto está bajo licencia. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Contacto y Soporte

Si encuentras algún problema o tienes sugerencias, no dudes en:

- **Abrir un Issue** en el repositorio
- **Contactar directamente**: david.salomon.nava11@gmail.com
- **Visitar nuestra documentación** completa en la [Wiki del proyecto](https://github.com/tuusuario/ecommerce_project/wiki)

## Agradecimientos

Este proyecto utiliza varias bibliotecas y servicios de código abierto sin los cuales no sería posible:

- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Stripe](https://stripe.com/)
- Y todos los contribuyentes que han ayudado a mejorar este proyecto

---

Desarrollado por FantazyLabz
