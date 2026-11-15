# Permite guardar los errores y resultados en un archivo.
import logging
# Importa lo necesario para crear clases abstractas.
from abc import ABC, abstractmethod
# Comprueba si un número decimal es válido.
from math import isfinite

# Guarda en el archivo la fecha, los resultados y los errores.
logging.basicConfig(filename='errores_sistema.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Error para datos de clientes o servicios que no son válidos.
class ErrorDatoInvalido(Exception):
    pass

# Error para reservas que no se pueden realizar.
class ErrorReserva(Exception):
    pass

# Clase general que pide mostrar la información en las clases hijas.
class EntidadSistema(ABC):
    # Señala el método que cada clase hija debe completar.
    @abstractmethod
    def mostrar_informacion(self) -> str:
        pass


# Cliente: comprueba los datos y mantiene privados el nombre y la identificación.
class Cliente(EntidadSistema):
    # Recibe la identificación y el nombre del cliente.
    def __init__(self, identificacion, nombre):
        # La identificación debe ser un texto con contenido.
        if not isinstance(identificacion, str) or not identificacion.strip():
            raise ErrorDatoInvalido("La identificación del cliente es obligatoria.")
        # El nombre debe ser un texto con contenido.
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorDatoInvalido("El nombre del cliente es obligatorio.")

        # Los dos guiones bajos mantienen los datos dentro de la clase.
        # Quita espacios sobrantes a la identificación.
        self.__identificacion = identificacion.strip()
        # Quita espacios sobrantes al nombre.
        self.__nombre = nombre.strip()

    # Permite consultar la identificación sin cambiarla.
    @property
    def identificacion(self):
        # Devuelve la identificación que quedó guardada.
        return self.__identificacion

    # Permite consultar el nombre sin cambiarlo.
    @property
    def nombre(self):
        # Devuelve el nombre que quedó guardado.
        return self.__nombre

    # Muestra los datos básicos del cliente.
    def mostrar_informacion(self) -> str:
        return f"Cliente: {self.nombre} (ID: {self.identificacion})"


# Clase general de los servicios.

class Servicio(EntidadSistema):
    # Cada servicio recibe un código y un costo base.
    def __init__(self, codigo, costo_base):
        # El código del servicio no puede estar vacío.
        if not isinstance(codigo, str) or not codigo.strip():
            raise ErrorDatoInvalido("El código del servicio es obligatorio.")

        # El costo debe ser un número, no un valor verdadero o falso.
        if isinstance(costo_base, bool) or not isinstance(costo_base, (int, float)):
            # Así evita comparar texto u otros datos con números.
            raise ErrorDatoInvalido("El costo base debe ser un número válido.")

        # No acepta valores como infinito o NaN.
        if isinstance(costo_base, float) and not isfinite(costo_base):
            raise ErrorDatoInvalido("El costo base debe ser un número finito.")
        # No se aceptan costos negativos.
        if costo_base < 0:
            raise ErrorDatoInvalido(f"El costo base no puede ser negativo para el servicio {codigo}.")

        self.codigo = codigo.strip()
        self.costo_base = costo_base

    # Comprueba el descuento y el impuesto antes de calcular el total.
    def validar_ajustes(
        self,
        subtotal: int | float,
        descuento: int | float = 0,
        impuesto: int | float = 0,
    ) -> int | float:
        # Comprueba que el subtotal sea un número decimal válido.
        if isinstance(subtotal, float) and not isfinite(subtotal):
            raise ErrorDatoInvalido("No fue posible calcular un costo válido.")
        # El descuento debe ser numérico.
        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)):
            raise ErrorDatoInvalido("El descuento debe ser un número válido.")
        # No se permiten descuentos negativos o infinitos.
        if (isinstance(descuento, float) and not isfinite(descuento)) or descuento < 0:
            raise ErrorDatoInvalido("El descuento no puede ser negativo ni infinito.")
        # El impuesto debe ser numérico.
        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)):
            raise ErrorDatoInvalido("El impuesto debe ser un número válido.")
        # No se permiten impuestos negativos o infinitos.
        if (isinstance(impuesto, float) and not isfinite(impuesto)) or impuesto < 0:
            raise ErrorDatoInvalido("El impuesto no puede ser negativo ni infinito.")
        # El descuento no puede ser mayor que el subtotal.
        if descuento > subtotal:
            raise ErrorDatoInvalido("El descuento no puede superar el costo del servicio.")
        # Calcula el total y comprueba que el resultado sea válido.
        total = subtotal - descuento + impuesto
        if isinstance(total, float) and not isfinite(total):
            raise ErrorDatoInvalido("El costo final debe ser un número finito.")
        return total

    # Cada tipo de servicio debe tener su propio cálculo de costo.
    @abstractmethod
    def calcular_costo_final(self, descuento: int | float = 0) -> int | float:
        pass

# Reserva de salas: el costo depende de las horas.

class ReservaSala(Servicio):
    # Recibe el número de horas de la reserva.
    def __init__(self, codigo, costo_base, horas):
        # Usa las comprobaciones del servicio general.
        super().__init__(codigo, costo_base)

        # Las horas deben ser números mayores que cero.
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or horas <= 0:
            raise ErrorDatoInvalido("Las horas de reserva deben ser mayores que cero.")

        # Rechaza horas infinitas o NaN.
        if isinstance(horas, float) and not isfinite(horas):
            raise ErrorDatoInvalido("Las horas deben ser un número finito.")
        self.horas = horas


    # Calcula el costo por horas y permite descuento e impuesto.
    def calcular_costo_final(
        self,
        descuento: int | float = 0,
        impuesto: int | float = 0,
    ) -> int | float:
        # Calcula el subtotal de la sala.
        subtotal = self.costo_base * self.horas
        # Comprueba los ajustes antes de devolver el costo.
        return self.validar_ajustes(subtotal, descuento, impuesto)

    # Muestra el código y el costo de la sala.
    def mostrar_informacion(self) -> str:
        return f"Sala {self.codigo} | Total: ${self.calcular_costo_final()}"

# Alquiler de equipos: el costo depende de los días.

class AlquilerEquipo(Servicio):
    # Recibe el número de días del alquiler.
    def __init__(self, codigo, costo_base, dias):
        # Usa la validación común de los servicios.
        super().__init__(codigo, costo_base)

        # Los días deben ser números mayores que cero.
        if isinstance(dias, bool) or not isinstance(dias, (int, float)) or dias <= 0:
            raise ErrorDatoInvalido("Los días de alquiler deben ser mayores que cero.")

        # Rechaza días infinitos o NaN.
        if isinstance(dias, float) and not isfinite(dias):
            raise ErrorDatoInvalido("Los días deben ser un número finito.")
        self.dias = dias

        
    # Calcula el alquiler y permite aplicar un descuento.
    def calcular_costo_final(self, descuento: int | float = 0) -> int | float:
        # Calcula el subtotal del alquiler.
        subtotal = self.costo_base * self.dias
        # Comprueba el descuento antes de dar el total.
        return self.validar_ajustes(subtotal, descuento)

    # Muestra el código y el costo del equipo.
    def mostrar_informacion(self) -> str:
        return f"Equipo {self.codigo} | Total: ${self.calcular_costo_final()}"

# Asesoría: tiene un costo fijo.
# Aprovecha el código y el costo de la clase Servicio.
class Asesoria(Servicio):
    # Permite aplicar un descuento al costo de la asesoría.
    def calcular_costo_final(self, descuento: int | float = 0) -> int | float:
        return self.validar_ajustes(self.costo_base, descuento)

    # Muestra el código y el costo de la asesoría.
    def mostrar_informacion(self) -> str:
        return f"Asesoría {self.codigo} | Total: ${self.calcular_costo_final()}"

# La reserva reúne al cliente, el servicio, la duración y el estado.
class Reserva:
    
    # Si no se escribe duración, se toma la del servicio.
    def __init__(self, cliente, servicio, duracion=None):
        # Comprueba que se reciba un cliente válido.
        if not isinstance(cliente, Cliente):
            raise ErrorReserva("Se requiere un cliente válido para crear la reserva.")
        # Comprueba que se reciba un servicio válido.
        if not isinstance(servicio, Servicio):
            raise ErrorReserva("Se requiere un servicio válido para crear la reserva.")

        # Usa la duración correspondiente a cada servicio.
        if duracion is None:
            # Para la sala, utiliza las horas registradas.
            if isinstance(servicio, ReservaSala):
                duracion = servicio.horas
            # Para el equipo, utiliza los días registrados.
            elif isinstance(servicio, AlquilerEquipo):
                duracion = servicio.dias
            # Para la asesoría, utiliza una duración de referencia de 1.
            else:
                duracion = 1

        # La duración debe ser un número mayor que cero.
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise ErrorReserva("La duración de la reserva debe ser un número mayor que cero.")
        # Rechaza duraciones infinitas o NaN.
        if isinstance(duracion, float) and not isfinite(duracion):
            raise ErrorReserva("La duración debe ser un número finito.")
        # La duración debe coincidir con las horas de la sala.
        if isinstance(servicio, ReservaSala) and duracion != servicio.horas:
            raise ErrorReserva("La duración debe coincidir con las horas de la sala.")
        # La duración debe coincidir con los días del alquiler.
        if isinstance(servicio, AlquilerEquipo) and duracion != servicio.dias:
            raise ErrorReserva("La duración debe coincidir con los días de alquiler.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        # Toda reserva empieza pendiente.
        self.estado = "Pendiente"

        
    # Confirma la reserva solo si está pendiente.
    def confirmar(self):
        if self.estado != "Pendiente":
            raise ErrorReserva("Solo se pueden confirmar reservas pendientes.")
        # Cambia el estado de la reserva a confirmada.
        self.estado = "Confirmada"
        return f"Confirmada reserva de {self.cliente.nombre} para {self.servicio.codigo}."

    # Cancela la reserva si no está cancelada o procesada.
    def cancelar(self):
        if self.estado == "Cancelada":
            raise ErrorReserva("La reserva ya se encontraba cancelada.")
        # No permite cancelar una reserva ya procesada.
        if self.estado == "Procesada":
            raise ErrorReserva("No se puede cancelar una reserva ya procesada.")
        self.estado = "Cancelada"
        # Devuelve un mensaje de cancelación.
        return f"Cancelada reserva de {self.cliente.nombre}."


    # Procesa una reserva confirmada y calcula el costo.
    def procesar(self):
        # No permite procesar reservas pendientes o canceladas.
        if self.estado != "Confirmada":
            raise ErrorReserva("Solo se pueden procesar reservas confirmadas.")

        # Si falla el cálculo, genera un error de reserva.
        try:
            # Cada servicio calcula su costo según su tipo.
            total = self.servicio.calcular_costo_final()
        # Conserva el error que causó el problema.
        except Exception as error:
            raise ErrorReserva("No fue posible procesar la reserva.") from error

        # Cambia el estado solo después de calcular el costo.
        self.estado = "Procesada"
        # Devuelve el costo de la reserva procesada.
        return f"Reserva procesada correctamente. Total: ${total}"


# Guarda clientes, servicios y reservas en listas.
class SistemaGestion:
    def __init__(self):
        # Lista para los clientes registrados.
        self.clientes = []
        # Lista para los servicios registrados.
        self.servicios = []
        # Lista para las reservas registradas.
        self.reservas = []

    # Solo registra objetos de la clase Cliente.
    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise ErrorDatoInvalido("El cliente no es válido.")
        # Guarda el cliente que pasó la validación.
        self.clientes.append(cliente)

    # Solo registra objetos de las clases de servicio.
    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ErrorDatoInvalido("El servicio no es válido.")
        # Guarda el servicio que pasó la validación.
        self.servicios.append(servicio)

    
    # Registra la reserva después de comprobar sus datos.
    def registrar_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ErrorReserva("La reserva no es válida.")

        # El cliente debe estar registrado en este sistema.
        if reserva.cliente not in self.clientes:
            raise ErrorReserva("El cliente no está registrado.")

        # Un servicio no registrado se considera no disponible.
        if reserva.servicio not in self.servicios:
            raise ErrorReserva("El servicio no está disponible.")

        # La reserva aceptada queda en la lista.
        self.reservas.append(reserva)

# Cada prueba se ejecuta por separado para continuar si ocurre un error.
def ejecutar_simulacion(numero_operacion, funcion_prueba):
    # Indica qué operación está comenzando.
    print(f"\n--- Operación {numero_operacion} ---")
    try:
        # Ejecuta la prueba y guarda el resultado.
        resultado = funcion_prueba()
    # Controla los errores de datos y reservas.
    except (ErrorDatoInvalido, ErrorReserva) as error:
        # Guarda el error en el archivo de registro.
        logging.error(f"Op {numero_operacion}: {error}")
        print(f"Fallo controlado: {error}")
    # También controla errores inesperados.
    except Exception as error_general:
        # Registra los errores inesperados para poder revisarlos.
        logging.critical(f"Error crítico Op {numero_operacion}: {error_general}", exc_info=True)
        print("Fallo crítico del sistema.")
    # El bloque else solo funciona cuando no hay error.
    else:
        # Si no hubo errores, muestra el resultado.
        print(f"Éxito: {resultado}")
        # Guarda también el resultado correcto.
        logging.info(f"Op {numero_operacion}: {resultado}")
    # Este bloque se ejecuta con o sin errores.
    finally:
        # Al final indica que terminó la operación.
        print("Fin de la operación.")

# 1. Cliente válido
def op1(): return Cliente("101", "Ana").mostrar_informacion()
# 2. Cliente inválido (sin nombre)
def op2(): return Cliente("102", "").mostrar_informacion()
# 3. Servicio válido (Sala)
def op3(): return ReservaSala("S1", 50000, 2).mostrar_informacion()
# 4. Servicio inválido (Costo negativo)
def op4(): return AlquilerEquipo("E1", -10000, 3).mostrar_informacion()
# 5. Servicio válido (Asesoría)
def op5(): return Asesoria("A1", 150000).mostrar_informacion()
# 6. Reserva válida

# Registra un cliente y una sala antes de confirmar la reserva.
def op6():
    c = Cliente("103", "Luis")
    # El precio de la sala es de 40000 por hora.
    s = ReservaSala("S2", 40000, 1)

    sistema = SistemaGestion()
    # Primero registra al cliente.
    sistema.registrar_cliente(c)
    # Después registra el servicio.
    sistema.registrar_servicio(s)

    r = Reserva(c, s)
    # Comprueba y agrega la reserva a la lista.
    sistema.registrar_reserva(r)

    return r.confirmar()

# 7. Reserva inválida (Sin servicio)
def op7(): return Reserva(Cliente("104", "Marta"), None).confirmar()
# 8. Cancelar reserva válida
def op8():
    r = Reserva(Cliente("105", "Pedro"), Asesoria("A2", 80000))
    return r.cancelar()
# 9. Error al cancelar reserva ya cancelada
# Intenta cancelar la misma reserva dos veces.
def op9():
    r = Reserva(Cliente("106", "Sofia"), AlquilerEquipo("E2", 20000, 1))
    r.cancelar()
    return r.cancelar()
# 10. Calcula el costo de una sala con descuento e impuesto opcionales
def op10():
    s = ReservaSala("S3", 60000, 2)
    # Aplica un descuento de 10000 y un impuesto de 5000.
    total = s.calcular_costo_final(descuento=10000, impuesto=5000)
    return f"Sala S3 con ajustes. Total: ${total}"

# Agrupa las primeras diez pruebas.
operaciones = [op1, op2, op3, op4, op5, op6, op7, op8, op9, op10]

# Ejecuta las primeras diez pruebas en orden.

for i, op in enumerate(operaciones, 1):
    ejecutar_simulacion(i, op)


# Comprueba qué pasa si el servicio no está registrado.
def op11():
    # Inicia un sistema nuevo para esta prueba.
    sistema = SistemaGestion()
    cliente = Cliente("107", "Carlos")
    # Crea una asesoría que no se agregará a la lista.
    servicio = Asesoria("A3", 90000)

    # Registra al cliente, pero no el servicio.
    sistema.registrar_cliente(cliente)

    reserva = Reserva(cliente, servicio)
    # Esta acción detecta que el servicio no está disponible.
    sistema.registrar_reserva(reserva)

    return reserva.confirmar()

ejecutar_simulacion(11, op11)



# Confirma y procesa correctamente una reserva.
def op12():
    cliente = Cliente("108", "Laura")
    servicio = Asesoria("A4", 90000)
    # Crea la reserva con duración de referencia igual a 1.
    reserva = Reserva(cliente, servicio, duracion=1)
    # La confirma antes de procesarla.
    reserva.confirmar()
    # Devuelve el resultado de procesar la reserva.
    return reserva.procesar()

ejecutar_simulacion(12, op12)


# Muestra un mensaje al terminar las doce pruebas.
print("\n--- SIMULACIÓN FINALIZADA CORRECTAMENTE ---")
