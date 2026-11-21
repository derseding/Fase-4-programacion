# Importación de librerías estándar necesarias para el sistema
import logging  # Permite registrar eventos y errores en un archivo de log
import math     # Permite validar valores numéricos finitos (isfinite)
import os       # Permite gestionar rutas y crear carpetas en el sistema operativo
import re       # Permite validar formatos de texto mediante expresiones regulares
from abc import ABC, abstractmethod  # Permite definir clases y métodos abstractos (POO)
from enum import Enum                # Permite crear enumeraciones para los estados de reserva


# ==============================================================================
# 1. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ==============================================================================

class SoftwareFJError(Exception):
    """Excepción base de la que heredan todos los errores controlados del sistema."""
    pass


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando se omite o se deja vacío un parámetro obligatorio."""
    pass


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no cumplen con las reglas de formato."""
    pass


class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando los parámetros de configuración o uso de un servicio son inválidos."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza al intentar confirmar un servicio que actualmente está inactivo."""
    pass


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando se intenta crear o procesar una reserva con datos inconsistentes."""
    pass


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta ejecutar una acción en un estado no permitido."""
    pass


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando los valores de impuestos, descuentos o totales no son coherentes."""
    pass


# ==============================================================================
# 2. CONFIGURACIÓN DEL ARCHIVO DE LOGS (REGISTRO DE AUDITORÍA Y ERRORES)
# ==============================================================================

# Construye la ruta absoluta hacia la carpeta 'logs/software_fj.log' junto al script
RUTA_LOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logs",
    "software_fj.log"
)

# Crea la carpeta 'logs' si aún no existe, evitando errores de directorio no encontrado
os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)

# Inicializa el registrador principal del sistema con nivel informativo (INFO)
log = logging.getLogger("SoftwareFJ")
log.setLevel(logging.INFO)

# Evita duplicar manejadores si el módulo se importa varias veces
if not log.handlers:
    # Configura la escritura del archivo de log con codificación UTF-8 para tildes y eñes
    archivo_log = logging.FileHandler(RUTA_LOG, encoding="utf-8")
    # Define el formato: Fecha y hora | Nivel del evento | Mensaje descriptivo
    archivo_log.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    log.addHandler(archivo_log)


# ==============================================================================
# 3. CLASE BASE ABSTRACTA Y CLASE CLIENTE
# ==============================================================================

class Entidad(ABC):
    """Clase abstracta base que asigna un identificador único autoincremental a cada objeto."""
    contador = 0  # Atributo de clase compartido para llevar el conteo global de entidades

    def __init__(self):
        Entidad.contador += 1       # Incrementa el contador global al instanciar
        self._id = Entidad.contador  # Asigna el ID único protegido al objeto

    @property
    def id(self):
        """Devuelve el identificador único de la entidad (solo lectura)."""
        return self._id

    @abstractmethod
    def describir(self):
        """Método obligatorio que cada subclase debe implementar para describirse."""
        pass


class Cliente(Entidad):
    """Representa un cliente del sistema con encapsulamiento y validación estricta de datos."""

    def __init__(self, nombre, documento, correo, telefono):
        # Valida y asigna cada atributo privado antes de registrar el ID en la superclase
        self.__nombre = self._validar_nombre(nombre)
        self.__documento = self._validar_documento(documento)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)
        super().__init__()  # Llama al constructor de Entidad para asignar el ID

    @staticmethod
    def _obligatorio(valor, campo):
        """Verifica que un campo no sea None ni una cadena vacía o solo espacios."""
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError(f"El campo {campo} es obligatorio")
        return str(valor).strip()

    @classmethod
    def _validar_nombre(cls, valor):
        """Valida que el nombre tenga al menos 3 caracteres y solo contenga letras y espacios."""
        valor = cls._obligatorio(valor, "nombre")
        if len(valor) < 3 or not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", valor):
            raise ClienteInvalidoError("El nombre no es valido")
        return valor

    @classmethod
    def _validar_documento(cls, valor):
        """Valida que el documento de identidad tenga entre 5 y 12 dígitos numéricos."""
        valor = cls._obligatorio(valor, "documento")
        if not re.fullmatch(r"\d{5,12}", valor):
            raise ClienteInvalidoError("El documento debe tener entre 5 y 12 numeros")
        return valor

    @classmethod
    def _validar_correo(cls, valor):
        """Valida que el correo electrónico cumpla con una estructura estándar usuario@dominio.ext."""
        valor = cls._obligatorio(valor, "correo")
        if not re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", valor):
            raise ClienteInvalidoError("El correo no tiene un formato valido")
        return valor

    @classmethod
    def _validar_telefono(cls, valor):
        """Valida que el número telefónico contenga entre 7 y 10 dígitos numéricos."""
        valor = cls._obligatorio(valor, "telefono")
        if not re.fullmatch(r"\d{7,10}", valor):
            raise ClienteInvalidoError("El telefono debe tener entre 7 y 10 numeros")
        return valor

    # Propiedades de lectura y actualización controlada (getters y setters)
    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, nuevo_correo):
        """Permite actualizar el correo validando nuevamente su formato."""
        self.__correo = self._validar_correo(nuevo_correo)

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, nuevo_telefono):
        """Permite actualizar el teléfono validando nuevamente su formato."""
        self.__telefono = self._validar_telefono(nuevo_telefono)

    def describir(self):
        """Retorna una ficha resumen legible con los datos del cliente."""
        return (
            f"Cliente #{self.id}: {self.nombre} | "
            f"Documento: {self.documento} | "
            f"{self.correo} | Telefono: {self.telefono}"
        )


# ==============================================================================
# 4. CLASE ABSTRACTA SERVICIO Y SUS ESPECIALIZACIONES
# ==============================================================================

class Servicio(Entidad, ABC):
    """Clase base abstracta para todos los servicios ofertados en el sistema."""
    IVA = 0.19  # Constante con la tarifa estándar de IVA (19%)

    def __init__(self, nombre, tarifa_hora, disponible=True):
        # Verifica que el nombre del servicio no esté vacío
        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError("El nombre del servicio es obligatorio")

        # Verifica que la tarifa sea un número real (no booleano), finito y mayor que cero
        if (
            not isinstance(tarifa_hora, (int, float))
            or isinstance(tarifa_hora, bool)
            or not math.isfinite(tarifa_hora)
            or tarifa_hora <= 0
        ):
            raise ServicioInvalidoError(
                "La tarifa por hora debe ser un numero mayor que cero"
            )

        super().__init__()  # Asigna el ID de entidad
        self._nombre = str(nombre).strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        """Cambia el estado de disponibilidad del servicio."""
        self._disponible = bool(valor)

    @abstractmethod
    def calcular_costo(self, horas):
        """Calcula el costo base del servicio según su lógica específica."""
        pass

    @abstractmethod
    def validar_parametros(self, horas):
        """Valida restricciones particulares del servicio (como límite de horas)."""
        pass

    @abstractmethod
    def describir(self):
        """Retorna una descripción detallada del servicio."""
        pass

    @staticmethod
    def _validar_horas(horas, maximo):
        """Comprueba que las horas sean un número válido, positivo y dentro del máximo permitido."""
        if (
            not isinstance(horas, (int, float))
            or isinstance(horas, bool)
            or not math.isfinite(horas)
            or horas <= 0
            or horas > maximo
        ):
            raise ServicioInvalidoError(
                f"Las horas deben ser mayores que 0 y no superar {maximo}"
            )

    def calcular_total(self, horas, *extras):
        """Calcula el valor final aplicando opcionalmente impuesto y descuento."""
        # Limita la cantidad de argumentos adicionales a máximo dos (impuesto y descuento)
        if len(extras) > 2:
            raise CalculoInconsistenteError(
                "Solo se permiten impuesto y descuento como datos adicionales"
            )

        # Asigna valores por defecto (0.0) si no se envían impuesto o descuento
        impuesto = extras[0] if len(extras) >= 1 else 0.0
        descuento = extras[1] if len(extras) == 2 else 0.0

        # Valida que tanto impuesto como descuento sean números finitos y no booleanos
        for valor in (impuesto, descuento):
            if (
                not isinstance(valor, (int, float))
                or isinstance(valor, bool)
                or not math.isfinite(valor)
            ):
                raise CalculoInconsistenteError(
                    "El impuesto y el descuento deben ser numeros validos"
                )

        # Verifica rangos lógicos: impuesto >= 0 y descuento entre 0% y menos del 100%
        if impuesto < 0 or descuento < 0 or descuento >= 1:
            raise CalculoInconsistenteError(
                "El impuesto no puede ser negativo y el descuento debe estar entre 0 y 1"
            )

        # Ejecuta la validación específica de horas de la subclase
        self.validar_parametros(horas)

        # Calcula el monto total aplicando impuesto y descuento
        total = self.calcular_costo(horas) * (1 + impuesto) * (1 - descuento)

        # Verifica que el resultado final sea numéricamente válido y positivo
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError("El total calculado no es valido")

        return round(total, 2)  # Redondea a dos decimales


class ReservaSala(Servicio):
    """Servicio especializado para el alquiler de salas por horas."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        # Valida que la capacidad sea un número entero positivo (descartando booleanos)
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ServicioInvalidoError(
                "La capacidad de la sala debe ser un entero positivo"
            )
        super().__init__(nombre, tarifa_hora, disponible)
        self._capacidad = capacidad

    def validar_parametros(self, horas):
        """Las salas se pueden reservar por un máximo de 12 horas continuas."""
        self._validar_horas(horas, 12)

    def calcular_costo(self, horas):
        """Calcula tarifa por horas y aplica un recargo del 15% si la capacidad supera 50 personas."""
        costo = self._tarifa_hora * horas
        if self._capacidad > 50:
            return costo * 1.15
        return costo

    def describir(self):
        return (
            f"Sala {self.nombre} | "
            f"Capacidad: {self._capacidad} | "
            f"Tarifa: ${self._tarifa_hora:,.0f}/hora"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para el préstamo de equipos tecnológicos."""

    def __init__(self, nombre, tarifa_hora, tipo_equipo, disponible=True):
        # Valida que se especifique la categoría o tipo de equipo
        if tipo_equipo is None or str(tipo_equipo).strip() == "":
            raise ParametroFaltanteError("Debe indicar que equipo se va a alquilar")
        super().__init__(nombre, tarifa_hora, disponible)
        self._tipo_equipo = str(tipo_equipo).strip()

    def validar_parametros(self, horas):
        """Los equipos se pueden alquilar hasta por 72 horas."""
        self._validar_horas(horas, 72)

    def calcular_costo(self, horas):
        """Calcula tarifa por horas más un cargo fijo de $20,000 por concepto de seguro."""
        return self._tarifa_hora * horas + 20000

    def describir(self):
        return (
            f"Equipo {self.nombre} ({self._tipo_equipo}) | "
            f"${self._tarifa_hora:,.0f}/hora mas seguro"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para consultorías técnicas según nivel de complejidad."""
    FACTORES = {
        "clasico": 1.0,
        "medio": 1.5,
        "plus": 2.0
    }

    def __init__(
        self,
        nombre,
        tarifa_hora,
        especialidad,
        nivel="clasico",
        disponible=True
    ):
        # Valida que la especialidad no esté vacía
        if especialidad is None or str(especialidad).strip() == "":
            raise ParametroFaltanteError("Debe indicar la especialidad de la asesoria")
        # Valida que el nivel exista dentro del diccionario FACTORES
        if nivel not in self.FACTORES:
            raise ServicioInvalidoError("El nivel debe ser clasico, medio o plus")
        super().__init__(nombre, tarifa_hora, disponible)
        self._especialidad = str(especialidad).strip()
        self._nivel = nivel

    def validar_parametros(self, horas):
        """Las asesorías tienen un límite máximo de 8 horas por sesión."""
        self._validar_horas(horas, 8)

    def calcular_costo(self, horas):
        """Multiplica tarifa base por horas y por el factor multiplicador del nivel."""
        return self._tarifa_hora * horas * self.FACTORES[self._nivel]

    def describir(self):
        return (
            f"Asesoria {self.nombre} | "
            f"{self._especialidad} | "
            f"Nivel: {self._nivel}"
        )


# ==============================================================================
# 5. ESTADOS Y GESTIÓN DEL CICLO DE VIDA DE UNA RESERVA
# ==============================================================================

class EstadoReserva(Enum):
    """Define los estados posibles dentro del flujo de una reserva."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(Entidad):
    """Vincula a un cliente con un servicio durante un tiempo determinado y controla su estado."""

    def __init__(self, cliente, servicio, horas):
        # Verifica que los objetos recibidos sean instancias válidas de Cliente y Servicio
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva necesita un cliente valido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva necesita un servicio valido")

        # Valida las horas según las reglas del servicio y encadena la excepción si falla
        try:
            servicio.validar_parametros(horas)
        except ServicioInvalidoError as error:
            raise ReservaInvalidaError(
                "No se pudo crear la reserva porque las horas no son validas"
            ) from error

        super().__init__()  # Asigna ID único a la reserva
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = EstadoReserva.PENDIENTE  # Toda reserva inicia en estado Pendiente
        self._total = None

    @property
    def estado(self):
        return self._estado

    @property
    def total(self):
        return self._total

    def confirmar(self):
        """Cambia el estado de PENDIENTE a CONFIRMADA si el servicio está disponible."""
        if self._estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                "Solo se puede confirmar una reserva pendiente"
            )
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio {self._servicio.nombre} no esta disponible"
            )
        self._estado = EstadoReserva.CONFIRMADA
        log.info("Reserva #%s confirmada", self.id)

    def cancelar(self):
        """Cancela la reserva siempre y cuando no haya sido cancelada ni procesada previamente."""
        if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                "Esta reserva no se puede cancelar en su estado actual"
            )
        self._estado = EstadoReserva.CANCELADA
        log.info("Reserva #%s cancelada", self.id)

    def procesar(self, impuesto=None, descuento=0.0):
        """Calcula el cobro final de una reserva confirmada y la marca como PROCESADA."""
        # Usa el IVA estándar del servicio si no se especifica otro impuesto
        impuesto = Servicio.IVA if impuesto is None else impuesto

        try:
            # Solo se pueden procesar reservas que ya fueron confirmadas
            if self._estado != EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    "Primero se debe confirmar la reserva"
                )
            total = self._servicio.calcular_total(self._horas, impuesto, descuento)
        except (CalculoInconsistenteError, ServicioInvalidoError) as error:
            # Encadena errores de cálculo dentro de ReservaInvalidaError
            raise ReservaInvalidaError(
                "No se pudo calcular el total de la reserva"
            ) from error
        else:
            # Si no hubo errores, guarda el total, actualiza estado y registra en log
            self._total = total
            self._estado = EstadoReserva.PROCESADA
            log.info("Reserva #%s procesada. Total: $%.2f", self.id, total)
            return total
        finally:
            # Se ejecuta siempre (con éxito o con error) para dejar traza de auditoría
            log.info("Termino el intento de procesar la reserva #%s", self.id)

    def describir(self):
        """Retorna el estado actual y el resumen económico de la reserva."""
        total = (
            f"${self._total:,.2f}"
            if self._total is not None
            else "Pendiente de calculo"
        )
        return (
            f"Reserva #{self.id} | "
            f"Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | "
            f"Horas: {self._horas} | "
            f"Estado: {self._estado.value} | "
            f"Total: {total}"
        )


# ==============================================================================
# 6. CLASE GESTORA DEL SISTEMA (FACHADA CON MANEJO CENTRALIZADO DE ERRORES)
# ==============================================================================

class GestorFJ:
    """Centraliza las operaciones del sistema capturando excepciones para evitar caídas."""

    def __init__(self):
        self.clientes = []   # Lista en memoria de clientes registrados
        self.servicios = []  # Lista en memoria de servicios creados
        self.reservas = []   # Lista en memoria de reservas generadas

    def registrar_cliente(self, **datos):
        """Intenta instanciar y registrar un cliente capturando errores de validación."""
        try:
            cliente = Cliente(**datos)
        except (SoftwareFJError, TypeError) as error:
            log.error("No se pudo registrar el cliente: %s", error)
            print(f"[ERROR] {error}")
            return None
        else:
            self.clientes.append(cliente)
            log.info("Cliente registrado: %s", cliente.describir())
            print(f"[OK] {cliente.describir()}")
            return cliente

    def crear_servicio(self, clase, *args, **kwargs):
        """Intenta instanciar y registrar cualquier subclase de Servicio."""
        try:
            servicio = clase(*args, **kwargs)
        except (SoftwareFJError, TypeError) as error:
            log.error("No se pudo crear el servicio: %s", error)
            print(f"[ERROR] {error}")
            return None
        else:
            self.servicios.append(servicio)
            log.info("Servicio creado: %s", servicio.describir())
            print(f"[OK] {servicio.describir()}")
            return servicio

    def crear_reserva(self, cliente, servicio, horas):
        """Intenta crear una reserva reportando tanto el error principal como su causa original."""
        try:
            reserva = Reserva(cliente, servicio, horas)
        except SoftwareFJError as error:
            causa = f" Causa original: {error.__cause__}" if error.__cause__ else ""
            log.error("No se pudo crear la reserva: %s%s", error, causa)
            print(f"[ERROR] {error}{causa}")
            return None
        else:
            self.reservas.append(reserva)
            log.info("Reserva creada: %s", reserva.describir())
            print(f"[OK] {reserva.describir()}")
            return reserva

    def ejecutar(self, accion, reserva, **datos):
        """Ejecuta dinámicamente una acción ('confirmar', 'cancelar', 'procesar') sobre una reserva."""
        try:
            if not isinstance(reserva, Reserva):
                raise ReservaInvalidaError(
                    "No hay una reserva valida para realizar esta operacion"
                )
            if accion not in ("confirmar", "cancelar", "procesar"):
                raise OperacionNoPermitidaError("La operacion solicitada no existe")

            # Invoca el método correspondiente sobre el objeto reserva
            resultado = getattr(reserva, accion)(**datos)

        except SoftwareFJError as error:
            causa = f" Causa original: {error.__cause__}" if error.__cause__ else ""
            log.error("Fallo la operacion %s: %s%s", accion, error, causa)
            print(f"[ERROR] {error}{causa}")
            return None
        except Exception as error:
            # Captura cualquier fallo imprevisto con traza completa en el archivo de log
            log.exception("Ocurrio un error inesperado en %s", accion)
            print(f"[ERROR INESPERADO] {error}")
            return None
        else:
            print(f"[OK] {reserva.describir()}")
            return resultado


# ==============================================================================
# 7. EJECUCIÓN SECUENCIAL Y PRUEBAS DE ROBUSTEZ DEL PROGRAMA
# ==============================================================================

def main():
    """Ejecuta una batería secuencial de pruebas para validar flujos exitosos y manejo de errores."""
    gestor = GestorFJ()
    log.info("===== INICIO DE LA SIMULACION =====")

    # PRUEBA 1: Registro exitoso de un cliente con todos sus datos válidos
    print("\n1. Registro de un cliente correcto")
    luis = gestor.registrar_cliente(
        nombre="Luis Hernan",
        documento="53002412",
        correo="Lucho00@gmail.com",
        telefono="3001234567"
    )

    # PRUEBA 2: Validación de formato de correo electrónico inválido
    print("\n2. Registro de un cliente con correo incorrecto")
    gestor.registrar_cliente(
        nombre="Juan Fuentes",
        documento="1023375272",
        correo="jfuentesolmos.///",
        telefono="3201112233"
    )

    # PRUEBA 3: Validación de parámetro obligatorio faltante (documento)
    print("\n3. Registro de un cliente sin documento")
    gestor.registrar_cliente(
        nombre="Patricia Olmos",
        correo="ipog@gmail.com",
        telefono="3109876543"
    )

    # PRUEBA 4: Creación de un servicio de sala con capacidad superior a 50 (aplica recargo del 15%)
    print("\n4. Creacion de una sala")
    sala = gestor.crear_servicio(ReservaSala, "Sala Innovacion", 50000, 60)

    # PRUEBA 5: Creación de un servicio de alquiler de equipo
    print("\n5. Creacion de un equipo")
    equipo = gestor.crear_servicio(AlquilerEquipo, "Portatil Pro", 8000, "Portatil")

    # PRUEBA 6: Creación de una asesoría especializada nivel medio (factor 1.5)
    print("\n6. Creacion de una asesoria")
    asesoria = gestor.crear_servicio(
        AsesoriaEspecializada,
        "Asesoria Cloud",
        90000,
        "Computacion en la nube",
        "medio"
    )

    # PRUEBA 7: Validación de tarifa negativa en un servicio
    print("\n7. Creacion de un servicio con tarifa negativa")
    gestor.crear_servicio(ReservaSala, "Sala Rota", -100, 10)

    # PRUEBA 8: Flujo completo exitoso (crear -> confirmar -> procesar con IVA y descuento)
    print("\n8. Reserva correcta: confirmar y calcular el total")
    reserva1 = gestor.crear_reserva(luis, sala, 3)
    gestor.ejecutar("confirmar", reserva1)
    gestor.ejecutar("procesar", reserva1, impuesto=0.19, descuento=0.10)

    # PRUEBA 9: Validación de límite máximo de horas en asesoría (máximo 8)
    print("\n9. Reserva con demasiadas horas para una asesoria")
    gestor.crear_reserva(luis, asesoria, 20)

    # PRUEBA 10: Validación de reserva sin una instancia válida de Cliente
    print("\n10. Reserva sin un cliente valido")
    gestor.crear_reserva(None, equipo, 5)

    # PRUEBA 11: Validación de disponibilidad al intentar confirmar un servicio inactivo
    print("\n11. Intento de reservar un equipo no disponible")
    equipo.disponible = False
    reserva2 = gestor.crear_reserva(luis, equipo, 10)
    gestor.ejecutar("confirmar", reserva2)

    # PRUEBA 12: Validación de transición de estados (procesar sin confirmar y doble cancelación)
    print("\n12. Intentos de operaciones en un orden incorrecto")
    gestor.ejecutar("procesar", reserva2)
    gestor.ejecutar("cancelar", reserva2)
    gestor.ejecutar("cancelar", reserva2)

    # PRUEBA 13: Validación de porcentaje de descuento fuera de rango (>= 1)
    print("\n13. Calculo con un descuento incorrecto")
    asesoria.disponible = True
    reserva3 = gestor.crear_reserva(luis, asesoria, 2)
    gestor.ejecutar("confirmar", reserva3)
    gestor.ejecutar("procesar", reserva3, impuesto=0.19, descuento=1.5)

    # PRUEBA 14: Validación de capacidad inválida (0) al crear una sala
    print("\n14. Creacion de sala con capacidad igual a cero")
    gestor.crear_servicio(ReservaSala, "Sala Vacia", 40000, 0)

    # PRUEBA 15: Validación de nivel de asesoría inexistente
    print("\n15. Creacion de asesoria con nivel no permitido")
    gestor.crear_servicio(
        AsesoriaEspecializada,
        "Asesoria Seguridad",
        85000,
        "Ciberseguridad",
        "experto"
    )

    # PRUEBA 16: Intento de cancelar una reserva que ya fue procesada
    print("\n16. Intento de cancelar una reserva ya procesada")
    gestor.ejecutar("cancelar", reserva1)

    # Resumen final de todas las reservas registradas en el sistema
    print("\n===== RESUMEN DE LAS RESERVAS =====")
    for reserva in gestor.reservas:
        print(reserva.describir())

    log.info("===== FIN DE LA SIMULACION =====")
    print("\nEl programa termino sin cerrarse por los errores")
    print(f"Los eventos y errores quedaron guardados en: {RUTA_LOG}")


# Punto de entrada principal cuando se ejecuta el archivo directamente
if __name__ == "__main__":
    main()
