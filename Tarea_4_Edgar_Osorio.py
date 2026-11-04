# Importa logging para registrar eventos exitosos y errores del programa
import logging
# Importa ABC y abstractmethod para definir clases y métodos abstractos
from abc import ABC, abstractmethod

# Guarda mensajes INFO, ERROR y CRITICAL en un archivo con fecha y hora
logging.basicConfig(filename='errores_sistema.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Error propio del programa para valores de clientes o servicios que no son válidos
class ErrorDatoInvalido(Exception):
    # La excepción no necesita más métodos: hereda de Exception.
    pass

# Error propio del programa para operaciones de reserva que no se pueden realizar
class ErrorReserva(Exception):
    # La excepción se diferencia por su tipo al capturarla con except.
    pass

# Clase base abstracta: obliga a las clases hijas a mostrar su información
class EntidadSistema(ABC):
    # El decorador indica que el método deberá existir en una clase concreta.
    @abstractmethod
    # Las clases derivadas implementan su propia forma de mostrar la información.
    def mostrar_informacion(self):
        pass


# Cliente: valida la entrada y conserva la identificación y el nombre como datos internos
class Cliente(EntidadSistema):
    # Al crear un cliente se reciben su identificación y nombre.
    def __init__(self, identificacion, nombre):
        # Si alguno de los campos está vacío, se impide el registro.
        if not identificacion or not nombre:
            # Arroja error si los datos están vacíos
            # Comunica por qué no puede construirse el cliente.
            raise ErrorDatoInvalido("Identificación y nombre del cliente son obligatorios.")

        # El prefijo __ mantiene estos atributos internos y evita el acceso directo habitual
        # Guarda la identificación dentro del objeto.
        self.__identificacion = identificacion
        # Guarda el nombre dentro del objeto.
        self.__nombre = nombre

    # Propiedad de solo lectura para consultar la identificación del cliente
    @property
    # Devuelve la identificación sin ofrecer un método para cambiarla.
    def identificacion(self):
        return self.__identificacion

    # Propiedad de solo lectura para consultar el nombre del cliente
    @property
    # Devuelve el nombre sin ofrecer un método para cambiarlo.
    def nombre(self):
        return self.__nombre

    # Forma un texto para visualizar los datos básicos del cliente.
    def mostrar_informacion(self):
        # La cadena incluye el nombre y la identificación.
        return f"Cliente: {self.nombre} (ID: {self.identificacion})"


# Clase base abstracta para todos los tipos de servicio

class Servicio(EntidadSistema):
    # Todo servicio recibe un código y un costo base.
    def __init__(self, codigo, costo_base):
        # Acepta costos numéricos; rechaza valores lógicos y datos de otros tipos
        # Evita comparar texto u otros tipos con números.
        if isinstance(costo_base, bool) or not isinstance(costo_base, (int, float)):
            # Explica que el costo debe proporcionarse como número.
            raise ErrorDatoInvalido("El costo base debe ser un número válido.")

        # Un costo numérico también debe ser mayor o igual a cero.
        if costo_base < 0:
            # Rechaza costos base negativos
            raise ErrorDatoInvalido(f"El costo base no puede ser negativo para el servicio {codigo}.")

        # Almacena el identificador de este servicio.
        self.codigo = codigo
        # Almacena el precio utilizado en los cálculos.
        self.costo_base = costo_base

    
    # Obliga a cada servicio derivado a proporcionar su cálculo.
    @abstractmethod
    # El descuento tiene valor inicial cero cuando no se indica.
    def calcular_costo_final(self, descuento=0):
        # El cálculo concreto se define en las clases hijas.
        pass

# Servicio 1: reserva de salas con un costo calculado por horas

    # Hereda las reglas comunes establecidas en Servicio.
class ReservaSala(Servicio):
    # El parámetro horas indica el tiempo de uso de la sala.
    def __init__(self, codigo, costo_base, horas):
        # Reutiliza la validación del costo base y guarda el código.
        super().__init__(codigo, costo_base)

        # Rechaza horas de reserva iguales a cero, negativas o no numéricas
        # Comprueba que las horas sean un número positivo.
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or horas <= 0:
            # Notifica cuando las horas no cumplen las condiciones.
            raise ErrorDatoInvalido("Las horas de reserva deben ser mayores que cero.")

        # Almacena la cantidad de horas de uso.
        self.horas = horas


    # Acepta un descuento y un impuesto opcionales.
    def calcular_costo_final(self, descuento=0, impuesto=0):
        # Multiplica costo por horas, resta descuento y suma impuesto.
        return (self.costo_base * self.horas) - descuento + impuesto

    # Devuelve la descripción de la sala y el costo calculado.
    def mostrar_informacion(self):
        return f"Sala {self.codigo} | Total: ${self.calcular_costo_final()}"

# Servicio 2: alquiler de equipos con un costo calculado por días

    # Hereda de Servicio y define el alquiler por días.
class AlquilerEquipo(Servicio):
    # El parámetro dias es el tiempo del alquiler.
    def __init__(self, codigo, costo_base, dias):
        # Valida primero los datos comunes del servicio.
        super().__init__(codigo, costo_base)

        # Rechaza días de alquiler iguales a cero, negativos o no numéricos
        # Solo se aceptan días representados por números positivos.
        if isinstance(dias, bool) or not isinstance(dias, (int, float)) or dias <= 0:
            # Comunica el error de duración del alquiler.
            raise ErrorDatoInvalido("Los días de alquiler deben ser mayores que cero.")

        # Guarda los días para calcular el importe.
        self.dias = dias

        
    # Calcula costo por día y descuenta el ajuste opcional.
    def calcular_costo_final(self, descuento=0):
        # El resultado es costo_base multiplicado por dias menos descuento.
        return (self.costo_base * self.dias) - descuento

    # Construye el texto visible para el alquiler del equipo.
    def mostrar_informacion(self):
        return f"Equipo {self.codigo} | Total: ${self.calcular_costo_final()}"

# Servicio 3: asesoría especializada; el costo no depende de días ni horas
    # Hereda código y costo base sin añadir otros parámetros.
class Asesoria(Servicio):
    # En la asesoría el costo final es el costo base menos descuento.
    def calcular_costo_final(self, descuento=0):
        return self.costo_base - descuento

    # Presenta el código y el costo final de la asesoría.
    def mostrar_informacion(self):
        return f"Asesoría {self.codigo} | Total: ${self.calcular_costo_final()}"

# Reserva: relaciona un cliente con un servicio, duración y estado
class Reserva:
    
    # La duración inicia en 1 si quien crea la reserva no indica otra.
    def __init__(self, cliente, servicio, duracion=1):
        # Valida que existan ambas referencias antes de crear la reserva.
        if not cliente or not servicio:
            # No permite crear una reserva si falta el cliente o el servicio
            raise ErrorReserva("Se requiere un cliente y un servicio válidos para crear la reserva.")

        # Solo permite duraciones numéricas mayores que cero.
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            # Rechaza duraciones inválidas antes de guardar la reserva
            raise ErrorReserva("La duración de la reserva debe ser un número mayor que cero.")

        # Asocia el cliente recibido a esta reserva.
        self.cliente = cliente
        # Asocia el servicio recibido a esta reserva.
        self.servicio = servicio
        # Guarda el valor de duración ya validado.
        self.duracion = duracion
        # Una reserva nueva comienza con estado Pendiente.
        self.estado = "Pendiente"

        
    # Confirma la reserva cuando no ha sido cancelada.
    def confirmar(self):
        # Revisa el estado actual para impedir una confirmación inválida.
        if self.estado == "Cancelada":
            # Rechaza la confirmación de una reserva cancelada
            raise ErrorReserva("No se puede confirmar una reserva que ya fue cancelada.")
        # Actualiza el estado una vez superada la validación.
        self.estado = "Confirmada"
        # Devuelve el texto que confirma cliente y servicio.
        return f"Confirmada reserva de {self.cliente.nombre} para {self.servicio.codigo}."

    # Cancela la reserva si todavía no se había cancelado.
    def cancelar(self):
        # Una segunda cancelación genera un error controlado.
        if self.estado == "Cancelada":
             # Evita cancelar una reserva que ya se encontraba cancelada
            raise ErrorReserva("La reserva ya se encontraba cancelada.")
        # Cambia el estado a Cancelada cuando la operación es válida.
        self.estado = "Cancelada"
        # Devuelve la confirmación de cancelación.
        return f"Cancelada reserva de {self.cliente.nombre}."


    # Procesa una reserva confirmada y calcula el importe correspondiente
    def procesar(self):
        # Una reserva pendiente o cancelada no puede procesarse.
        if self.estado != "Confirmada":
            raise ErrorReserva("Solo se pueden procesar reservas confirmadas.")

        # Aísla un posible fallo al calcular el costo.
        try:
            # Solicita al servicio su cálculo de costo según el tipo de servicio
            total = self.servicio.calcular_costo_final()
        # Captura problemas producidos dentro del cálculo del servicio.
        except Exception as error:
            # Conserva la causa del fallo usando encadenamiento de excepciones (from)
            # Lanza ErrorReserva conservando el error original como causa.
            raise ErrorReserva("No fue posible procesar la reserva.") from error

        # Solo después del cálculo cambia el estado a Procesada.
        self.estado = "Procesada"
        # Informa el valor calculado por el servicio.
        return f"Reserva procesada correctamente. Total: ${total}"


# SistemaGestion: almacena en listas los clientes, servicios y reservas registrados
class SistemaGestion:
    # Cada instancia administra tres listas independientes.
    def __init__(self):
        # Lista de clientes admitidos por el sistema.
        self.clientes = []
        # Lista de servicios admitidos por el sistema.
        self.servicios = []
        # Lista de reservas creadas correctamente.
        self.reservas = []

    # Añade un cliente solo si es un objeto de la clase Cliente.
    def registrar_cliente(self, cliente):
        # Impide registrar valores que no sean clientes.
        if not isinstance(cliente, Cliente):
            raise ErrorDatoInvalido("El cliente no es válido.")
        # Agrega el objeto válido a la lista de clientes.
        self.clientes.append(cliente)

    # Añade un servicio solo si proviene de Servicio o de una clase hija.
    def registrar_servicio(self, servicio):
        # Impide registrar valores ajenos a los servicios previstos.
        if not isinstance(servicio, Servicio):
            raise ErrorDatoInvalido("El servicio no es válido.")
        # Agrega el servicio aceptado a la lista.
        self.servicios.append(servicio)

    
    # Registra una reserva de un servicio previamente agregado.
    def registrar_reserva(self, reserva):
        # Comprueba que se haya creado un objeto Reserva.
        if not isinstance(reserva, Reserva):
            raise ErrorReserva("La reserva no es válida.")

        # En esta simulación, un servicio no registrado se considera no disponible
        # El servicio debe existir dentro de la lista de esta instancia.
        if reserva.servicio not in self.servicios:
            # Rechaza el registro si el servicio no está en la lista.
            raise ErrorReserva("El servicio no está disponible.")

        # Una reserva aceptada se añade a la lista de reservas.
        self.reservas.append(reserva)


# --- SIMULACIONES: 12 OPERACIONES (LA GUÍA EXIGE AL MENOS 10) ---

# Ejecuta cada prueba por separado para que un error no detenga a las demás
    # Recibe el número y la función de la operación que se va a comprobar.
def ejecutar_simulacion(numero_operacion, funcion_prueba):
    # Muestra qué operación está comenzando.
    print(f"\n--- Operación {numero_operacion} ---")
    # Protege la ejecución de esta operación de posibles excepciones.
    try:
        # Intenta ejecutar la acción
        # Invoca la prueba recibida y almacena su resultado.
        resultado = funcion_prueba()
    # Captura errores esperados de datos o de reservas.
    except (ErrorDatoInvalido, ErrorReserva) as error:
        # Registra las excepciones personalizadas en el archivo de eventos
        # Guarda la causa con el número de operación en el log.
        logging.error(f"Op {numero_operacion}: {error}")
        # Informa el fallo sin interrumpir las demás pruebas.
        print(f"Fallo controlado: {error}")
    # Captura otros errores que puedan aparecer durante las pruebas.
    except Exception as error_general:
        # Registra como crítico cualquier error diferente a las excepciones previstas
        # Escribe el mensaje del fallo inesperado en el registro.
        logging.critical(f"Error crítico Op {numero_operacion}: {error_general}")
        # Muestra una notificación general del fallo inesperado.
        print("Fallo crítico del sistema.")
    # Esta parte solo se ejecuta cuando la prueba termina sin excepción.
    else:
        # Cuando no ocurre un error, informa el resultado en pantalla y en el registro
        # Muestra por pantalla la descripción del resultado.
        print(f"Éxito: {resultado}")
        # Almacena el resultado exitoso con nivel INFO.
        logging.info(f"Op {numero_operacion}: {resultado}")
    # Cierra la operación tanto si hubo éxito como si hubo error.
    finally:
        # Se ejecuta al final de cada intento, haya tenido éxito o haya fallado
        # Confirma visualmente que terminó la operación.
        print("Fin de la operación.")

# Las operaciones 1 a 10 cubren el mínimo de simulaciones solicitado
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

    # Crea cliente, servicio y reserva para comprobar un registro válido.
def op6():
    # Crea al cliente Luis.
    c = Cliente("103", "Luis")
    # Crea una sala con costo de 40000 por una hora.
    s = ReservaSala("S2", 40000, 1)

    # Prepara una instancia de gestión para esta simulación.
    sistema = SistemaGestion()
    # Registra al cliente en la lista correspondiente.
    sistema.registrar_cliente(c)
    # Registra el servicio de sala en su lista.
    sistema.registrar_servicio(s)

    # Crea una reserva que reúne el cliente y el servicio registrados.
    r = Reserva(c, s)
    # Añade la reserva a la lista después de comprobar el servicio.
    sistema.registrar_reserva(r)

    # Confirma la reserva y devuelve el mensaje de éxito.
    return r.confirmar()

# 7. Reserva inválida (Sin servicio)
def op7(): return Reserva(Cliente("104", "Marta"), None).confirmar()
# 8. Cancelar reserva válida
    # Crea una reserva válida y solicita su cancelación.
def op8():
    # Construye una reserva de asesoría para Pedro.
    r = Reserva(Cliente("105", "Pedro"), Asesoria("A2", 80000))
    # La cancelación válida devuelve un texto de confirmación.
    return r.cancelar()
# 9. Error al cancelar reserva ya cancelada
    # Intenta cancelar dos veces una misma reserva.
def op9():
    # Prepara una reserva de alquiler para Sofía.
    r = Reserva(Cliente("106", "Sofia"), AlquilerEquipo("E2", 20000, 1))
    # La primera cancelación funciona.
    r.cancelar()
    # La segunda cancelación produce ErrorReserva.
    return r.cancelar() # Esto dispara el error
# 10. Calcula una reserva de sala con descuento e impuesto opcionales
    # Evalúa el costo con los parámetros opcionales del método.
def op10():
    # Crea una sala con costo de 60000 por hora durante dos horas.
    s = ReservaSala("S3", 60000, 2)
    # Aplica 10000 de descuento y 5000 de impuesto.
    total = s.calcular_costo_final(descuento=10000, impuesto=5000)
    # Devuelve un texto con el importe obtenido.
    return f"Sala S3 con ajustes. Total: ${total}"

# Agrupa las primeras diez funciones de prueba para ejecutarlas en orden
    # Esta lista contiene las funciones, no los resultados de las pruebas.
operaciones = [op1, op2, op3, op4, op5, op6, op7, op8, op9, op10]

# Recorre las diez pruebas de la lista y asigna un número a cada una

    # Enumerate entrega posición (desde 1) y función para cada caso.
for i, op in enumerate(operaciones, 1):
    # Ejecuta las primeras diez simulaciones en el orden definido.
    ejecutar_simulacion(i, op)


# 11. Comprueba el rechazo de una reserva con servicio no registrado
    # Usa una instancia independiente del sistema para este caso.
def op11():
    # Parte de listas vacías para simular la disponibilidad de servicios.
    sistema = SistemaGestion()
    # Crea el cliente que intenta reservar.
    cliente = Cliente("107", "Carlos")
    # Crea una asesoría que NO se agregará a la lista de servicios.
    servicio = Asesoria("A3", 90000)

    # El cliente se agrega correctamente al sistema.
    sistema.registrar_cliente(cliente)

    # No se registra el servicio para representar el caso de no disponibilidad
    # Forma una reserva para un servicio que no se registró.
    reserva = Reserva(cliente, servicio)
    # Aquí se detecta y comunica la falta de disponibilidad.
    sistema.registrar_reserva(reserva)

    # Solo devolvería confirmación si el registro fuese válido.
    return reserva.confirmar()

# Ejecuta por separado la prueba del servicio no disponible.
ejecutar_simulacion(11, op11)



# 12. Comprueba la confirmación y el procesamiento de una reserva válida
    # Crea y confirma una reserva válida antes de procesarla.
def op12():
    # Construye el cliente Laura.
    cliente = Cliente("108", "Laura")
    # Construye el servicio de asesoría.
    servicio = Asesoria("A4", 90000)
    # Crea la reserva con duración igual a 1.
    reserva = Reserva(cliente, servicio, duracion=1)
    # La confirma para permitir el procesamiento posterior.
    reserva.confirmar()
    # Procesa la reserva y devuelve el costo calculado.
    return reserva.procesar()

# Ejecuta la prueba de procesamiento de la operación 12.
ejecutar_simulacion(12, op12)


# Presenta un mensaje de cierre después de terminar todas las pruebas.
print("\n--- SIMULACIÓN FINALIZADA CORRECTAMENTE ---")
