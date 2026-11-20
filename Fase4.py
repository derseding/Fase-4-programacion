import logging
import math
import os
import re
from abc import ABC, abstractmethod
from enum import Enum

class SoftwareFJError(Exception):
    "Error general del sistema"

class ParametroFaltanteError(SoftwareFJError):
    pass
    "Se omitio un parametro obligatorio "

class ClienteInvalidoError(SoftwareFJError):
    pass
    "Datos de cliente invalidos"

class ServicioInvalidoError(SoftwareFJError):
    pass
    "Parametros de servicio invalidos"

class ServicioNoDisponibleError(SoftwareFJError):
    pass
    "El servicio solicitado no esta disponible"

class ReservaInvalidaError(SoftwareFJError):
    pass
    "Intento de reserva incorrecto"

class OperacionNoPermitidaError(SoftwareFJError):
    pass
    "Operacin no permitida"

class CalculoInconsistenteError(SoftwareFJError):
    pass
    "Calculo de costos con resultados inconsistentes"

#ARCHIVO PARA GUARDAR LOS EVENTOS Y LOS ERRORES

RUTA_LOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logs",
    "software_fj.log"
)
os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)
log = logging.getLogger("SoftwareFJ")
log.setLevel(logging.INFO)
if not log.handlers:
    archivo_log = logging.FileHandler(
        RUTA_LOG,
        encoding="utf-8"
    )
    archivo_log.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )
    log.addHandler(archivo_log)

#CLASE GENERAL Y CLASE CLIENTE

class Entidad(ABC):
    "Se crea un identificador para cada objeto"
    contador = 0
    def __init__(self):
        Entidad.contador += 1
        self._id = Entidad.contador
    @property
    def id(self):
        return self._id
    @abstractmethod
    def describir(self):
        pass

class Cliente(Entidad):
    "Guarda los datos del cliente y revisa que sean validos"
    def __init__(self, nombre, documento, correo, telefono):
        self.__nombre = self._validar_nombre(nombre)
        self.__documento = self._validar_documento(documento)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)
        super().__init__()

    #REVISA QUE LOS DATOS NO ESTEN VACIOS

    @staticmethod
    def _obligatorio(valor, campo):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError(
                f"El campo {campo} es obligatorio"
            )
        return str(valor).strip()
    
    # REVISA EL NOMBRE

    @classmethod
    def _validar_nombre(cls, valor):
        valor = cls._obligatorio(valor, "nombre")
        if len(valor) < 3 or not re.fullmatch(
            r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", valor
        ):
            raise ClienteInvalidoError(
                "El nombre no es valido"
            )
        return valor

    # REVISA EL DOCUMENTO

    @classmethod
    def _validar_documento(cls, valor):
        valor = cls._obligatorio(valor, "documento")
        if not re.fullmatch(r"\d{5,12}", valor):
            raise ClienteInvalidoError(
                "El documento debe tener entre 5 y 12 numeros"
            )
        return valor

    # REVISA EL CORREO

    @classmethod
    def _validar_correo(cls, valor):
        valor = cls._obligatorio(valor, "correo")
        if not re.fullmatch(
            r"[\w.+-]+@[\w-]+(\.[\w-]+)+", valor
        ):
            raise ClienteInvalidoError(
                "El correo no tiene un formato valido"
            )

        return valor

    # REVISA EL TELEFONO

    @classmethod
    def _validar_telefono(cls, valor):
        valor = cls._obligatorio(valor, "telefono")
        if not re.fullmatch(r"\d{7,10}", valor):
            raise ClienteInvalidoError(
                "El telefono debe tener entre 7 y 10 numeros"
            )
        return valor

    # PERMITE CONSULTAR LOS DATOS

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
        self.__correo = self._validar_correo(nuevo_correo)

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, nuevo_telefono):
        self.__telefono = self._validar_telefono(
            nuevo_telefono
        )
    def describir(self):
        return (
            f"Cliente #{self.id}: {self.nombre} | "
            f"Documento: {self.documento} | "
            f"{self.correo} | Telefono: {self.telefono}"
        )

# 4. CLASE GENERAL DE SERVICIOS

class Servicio(Entidad, ABC):
    IVA = 0.19
    def __init__(self, nombre, tarifa_hora, disponible=True):

        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError(
                "El nombre del servicio es obligatorio"
            )

        if (
            not isinstance(tarifa_hora, (int, float))
            or isinstance(tarifa_hora, bool)
            or not math.isfinite(tarifa_hora)
            or tarifa_hora <= 0
        ):
            raise ServicioInvalidoError(
                "La tarifa por hora debe ser un numero mayor que cero"
            )
        super().__init__()
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
        self._disponible = bool(valor)

    @abstractmethod
    def calcular_costo(self, horas):
        pass

    @abstractmethod
    def validar_parametros(self, horas):
        pass

    @abstractmethod
    def describir(self):
        pass

    #REVISA QUE LAS HORAS SEAN VALIDAS

    @staticmethod
    def _validar_horas(horas, maximo):
        if (
            not isinstance(horas, (int, float))
            or isinstance(horas, bool)
            or not math.isfinite(horas)
            or horas <= 0
            or horas > maximo
        ):
            raise ServicioInvalidoError(
                f"Las horas deben ser mayores que 0 "
                f"y no superar {maximo}"
            )

    #CALCULA EL TOTAL CON IMPUESTOS Y DESCUENTOS

    def calcular_total(self, horas, *extras):

        if len(extras) > 2:
            raise CalculoInconsistenteError(
                "Solo se permiten impuesto y descuento "
                "como datos adicionales"
            )
        impuesto = extras[0] if len(extras) >= 1 else 0.0
        descuento = extras[1] if len(extras) == 2 else 0.0
        for valor in (impuesto, descuento):
            if (
                not isinstance(valor, (int, float))
                or isinstance(valor, bool)
                or not math.isfinite(valor)
            ):
                raise CalculoInconsistenteError(
                    "El impuesto y el descuento "
                    "deben ser numeros validos"
                )
        if impuesto < 0 or descuento < 0 or descuento >= 1:
            raise CalculoInconsistenteError(
                "El impuesto no puede ser negativo y el "
                "descuento debe estar entre 0 y 1"
            )
        self.validar_parametros(horas)
        total = (
            self.calcular_costo(horas)
            * (1 + impuesto)
            * (1 - descuento)
        )
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(
                "El total calculado no es valido"
            )
        return round(total, 2)


 #SERVICIO DE RESERVA DE SALAS

class ReservaSala(Servicio):
    def __init__(
        self, nombre, tarifa_hora, capacidad, disponible=True
    ):
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
        self._validar_horas(horas, 12)

    def calcular_costo(self, horas):

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

#SERVICIO DE ALQUILER DE EQUIPOS

class AlquilerEquipo(Servicio):
    def __init__(
        self, nombre, tarifa_hora, tipo_equipo, disponible=True
    ):

        if tipo_equipo is None or str(tipo_equipo).strip() == "":
            raise ParametroFaltanteError(
                "Debe indicar que equipo se va a alquilar"
            )
        super().__init__(nombre, tarifa_hora, disponible)

        self._tipo_equipo = str(tipo_equipo).strip()
    def validar_parametros(self, horas):
        self._validar_horas(horas, 72)
    def calcular_costo(self, horas):
        return self._tarifa_hora * horas + 20000
    def describir(self):
        return (
            f"Equipo {self.nombre} ({self._tipo_equipo}) | "
            f"${self._tarifa_hora:,.0f}/hora mas seguro"
        )
    
# SERVICIO DE ASESORIAS
class AsesoriaEspecializada(Servicio):
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
        if especialidad is None or str(especialidad).strip() == "":
            raise ParametroFaltanteError(
                "Debe indicar la especialidad de la asesoria"
            )
        if nivel not in self.FACTORES:
            raise ServicioInvalidoError(
                "El nivel debe ser clasico, medio o plus"
            )
        super().__init__(nombre, tarifa_hora, disponible)
        self._especialidad = str(especialidad).strip()
        self._nivel = nivel
    def validar_parametros(self, horas):
        self._validar_horas(horas, 8)

    def calcular_costo(self, horas):
        return (
            self._tarifa_hora
            * horas
            * self.FACTORES[self._nivel]
        )

    def describir(self):
        return (
            f"Asesoria {self.nombre} | "
            f"{self._especialidad} | "
            f"Nivel: {self._nivel}"
        )

#ESTADOS DE LAS RESERVAS

class EstadoReserva(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"

#CLASE RESERVA

class Reserva(Entidad):
    def __init__(self, cliente, servicio, horas):
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError(
                "La reserva necesita un cliente valido"
            )
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError(
                "La reserva necesita un servicio valido"
            )
        try:
            servicio.validar_parametros(horas)
        except ServicioInvalidoError as error:

            raise ReservaInvalidaError(
                "No se pudo crear la reserva porque"
                "las horas no son validas"
            ) from error
        super().__init__()
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = EstadoReserva.PENDIENTE
        self._total = None
    @property
    def estado(self):
        return self._estado

    @property
    def total(self):
        return self._total

    #CONFIRMAR RESERVA

    def confirmar(self):

        if self._estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                "Solo se puede confirmar una reserva pendiente"
            )
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio {self._servicio.nombre} "
                "no esta disponible"
            )
        self._estado = EstadoReserva.CONFIRMADA
        log.info("Reserva #%s confirmada", self.id)

    #CANCELAR RESERVA

    def cancelar(self):

        if self._estado in (
            EstadoReserva.CANCELADA,
            EstadoReserva.PROCESADA
        ):
            raise OperacionNoPermitidaError(
                "Esta reserva no se puede cancelar "
                "en su estado actual"
            )
        self._estado = EstadoReserva.CANCELADA
        log.info("Reserva #%s cancelada", self.id)

    #PROCESAR RESERVA Y CALCULAR EL TOTAL

    def procesar(self, impuesto=None, descuento=0.0):
        impuesto = (
            Servicio.IVA if impuesto is None else impuesto
        )
        try:
            if self._estado != EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    "Primero se debe confirmar la reserva"
                )
            total = self._servicio.calcular_total(
                self._horas,
                impuesto,
                descuento
            )
        except (
            CalculoInconsistenteError,
            ServicioInvalidoError
        ) as error:
            raise ReservaInvalidaError(
                "No se pudo calcular el total de la reserva"
            ) from error
        else:
            self._total = total
            self._estado = EstadoReserva.PROCESADA

            log.info(
                "Reserva #%s procesada. Total: $%.2f",
                self.id,
                total
            )

            return total
        finally:
            log.info(
                "Termino el intento de procesar la reserva #%s",
                self.id
            )
    def describir(self):
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
#GESTOR DEL SISTEMA

class GestorFJ:
    def __init__(self):

        self.clientes = []
        self.servicios = []
        self.reservas = []
    #REGISTRAR CLIENTES
    def registrar_cliente(self, **datos):
        try:
            cliente = Cliente(**datos)
        except (SoftwareFJError, TypeError) as error:
            log.error(
                "No se pudo registrar el cliente: %s",
                error
            )
            print(f"[ERROR] {error}")
            return None
        else:
            self.clientes.append(cliente)
            log.info(
                "Cliente registrado: %s",
                cliente.describir()
            )
            print(f"[OK] {cliente.describir()}")
            return cliente
        
    #CREAR SERVICIOS

    def crear_servicio(self, clase, *args, **kwargs):
        try:
            servicio = clase(*args, **kwargs)
        except (SoftwareFJError, TypeError) as error:
            log.error(
                "No se pudo crear el servicio: %s",
                error
            )
            print(f"[ERROR] {error}")
            return None
        else:

            self.servicios.append(servicio)
            log.info(
                "Servicio creado: %s",
                servicio.describir()
            )
            print(f"[OK] {servicio.describir()}")
            return servicio

    #CREAR RESERVAS

    def crear_reserva(self, cliente, servicio, horas):
        try:

            reserva = Reserva(cliente, servicio, horas)
        except SoftwareFJError as error:
            causa = (
                f" Causa original: {error.__cause__}"
                if error.__cause__
                else ""
            )
            log.error(
                "No se pudo crear la reserva: %s%s",
                error,
                causa
            )
            print(f"[ERROR] {error}{causa}")
            return None
        else:
            self.reservas.append(reserva)

            log.info(
                "Reserva creada: %s",
                reserva.describir()
            )
            print(f"[OK] {reserva.describir()}")

            return reserva

    #EJECUTAR LAS OPERACIONES DE UNA RESERVA

    def ejecutar(self, accion, reserva, **datos):
        try:
            if not isinstance(reserva, Reserva):
                raise ReservaInvalidaError(
                    "No hay una reserva valida para "
                    "realizar esta operacion"
                )

            if accion not in (
                "confirmar",
                "cancelar",
                "procesar"
            ):
                raise OperacionNoPermitidaError(
                    "La operacion solicitada no existe"
                )

            resultado = getattr(reserva, accion)(**datos)

        except SoftwareFJError as error:

            causa = (
                f" Causa original: {error.__cause__}"
                if error.__cause__
                else ""
            )
            log.error(
                "Fallo la operacion %s: %s%s",
                accion,
                error,
                causa
            )
            print(f"[ERROR] {error}{causa}")
            return None
        except Exception as error:

            log.exception(
                "Ocurrio un error inesperado en %s",
                accion
            )
            print(f"[ERROR INESPERADO] {error}")

            return None
        else:
            print(f"[OK] {reserva.describir()}")

            return resultado


# PRUEBAS DEL PROGRAMA

def main():

    gestor = GestorFJ()

    log.info("===== INICIO DE LA SIMULACION =====")
    # PRUEBA 1: CLIENTE CORRECTO

    print("\n1. Registro de un cliente correcto")

    luis = gestor.registrar_cliente(
        nombre="Luis Hernan",
        documento="53002412",
        correo="Lucho00@gmail.com",
        telefono="3001234567"
    )

    # PRUEBA 2: CORREO INCORRECTO

    print("\n2. Registro de un cliente con correo incorrecto")

    gestor.registrar_cliente(
        nombre="Juan Fuentes",
        documento="1023375272",
        correo="jfuentesolmos.///",
        telefono="3201112233"
    )

    # PRUEBA 3: DOCUMENTO FALTANTE

    print("\n3. Registro de un cliente sin documento")

    gestor.registrar_cliente(
        nombre="Patricia Olmos",
        correo="ipog@gmail.com",
        telefono="3109876543"
    )

    # PRUEBA 4: CREAR UNA SALA

    print("\n4. Creacion de una sala")

    sala = gestor.crear_servicio(
        ReservaSala,
        "Sala Innovacion",
        50000,
        60
    )

    # PRUEBA 5: CREAR UN EQUIPO

    print("\n5. Creacion de un equipo")
    equipo = gestor.crear_servicio(
        AlquilerEquipo,
        "Portatil Pro",
        8000,
        "Portatil"
    )

    # PRUEBA 6: CREAR UNA ASESORIA

    print("\n6. Creacion de una asesoria")
    asesoria = gestor.crear_servicio(
        AsesoriaEspecializada,
        "Asesoria Cloud",
        90000,
        "Computacion en la nube",
        "medio"
    )

    # PRUEBA 7: TARIFA NEGATIVA

    print("\n7. Creacion de un servicio con tarifa negativa")

    gestor.crear_servicio(
        ReservaSala,
        "Sala Rota",
        -100,
        10
    )

    # PRUEBA 8: RESERVA CORRECTA

    print("\n8. Reserva correcta: confirmar y calcular el total")
    reserva1 = gestor.crear_reserva(
        luis,
        sala,
        3
    )

    gestor.ejecutar("confirmar", reserva1)

    gestor.ejecutar(
        "procesar",
        reserva1,
        impuesto=0.19,
        descuento=0.10
    )

    # PRUEBA 9: DEMASIADAS HORAS

    print("\n9. Reserva con demasiadas horas para una asesoria")

    gestor.crear_reserva(
        luis,
        asesoria,
        20
    )

    # PRUEBA 10: CLIENTE NO VALIDO
    print("\n10. Reserva sin un cliente valido")

    gestor.crear_reserva(
        None,
        equipo,
        5
    )

    # PRUEBA 11: SERVICIO NO DISPONIBLE
    print("\n11. Intento de reservar un equipo no disponible")

    equipo.disponible = False
    reserva2 = gestor.crear_reserva(
        luis,
        equipo,
        10
    )
    gestor.ejecutar("confirmar", reserva2)

    # PRUEBA 12: OPERACIONES INCORRECTAS

    print("\n12. Intentos de operaciones en un orden incorrecto")
    gestor.ejecutar("procesar", reserva2)
    gestor.ejecutar("cancelar", reserva2)
    gestor.ejecutar("cancelar", reserva2)

    # PRUEBA 13: DESCUENTO INCORRECTO

    print("\n13. Calculo con un descuento incorrecto")

    asesoria.disponible = True
    reserva3 = gestor.crear_reserva(
        luis,
        asesoria,
        2
    )
    gestor.ejecutar("confirmar", reserva3)

    gestor.ejecutar(
        "procesar",
        reserva3,
        impuesto=0.19,
        descuento=1.5
    )

    #RESUMEN FINAL

    print("\n===== RESUMEN DE LAS RESERVAS =====")

    for reserva in gestor.reservas:
        print(reserva.describir())

    log.info("===== FIN DE LA SIMULACION =====")

    print("\nEl programa termino sin cerrarse por los errores")

    print(
        "Los eventos y errores quedaron guardados en: "
        f"{RUTA_LOG}"
    )


if __name__ == "__main__":
    main()
